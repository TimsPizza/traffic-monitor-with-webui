from collections import deque
from threading import Lock, Thread, Event
import logging
from typing import Dict, Generic, Optional, TypeVar, Union
import signal
import time

from utils.Interfaces import (
    DynamicQueueResizeStrategy,
    BaseDynamicQueueResizeStrategy,
)

T = TypeVar("T")


class DynamicQueue(Generic[T]):
    def __init__(
        self,
        min_size: int = 1e3,
        max_size: int = 1e5,
        growth_factor: float = 1.5,
        shrink_factor: float = 0.5,
        # specify batch size for resizing check
        process_batch_size: int = 10,
        strategy: BaseDynamicQueueResizeStrategy = None,
        queue_id: Optional[str] = None,
    ):
        self._name = (
            f"{self.__class__.__name__}-{queue_id}"
            if queue_id
            else self.__class__.__name__
        )
        if min_size <= 0 or max_size <= 0 or min_size >= max_size:
            raise ValueError("Invalid queue size parameters")
        if growth_factor <= 1.0 or shrink_factor >= 1.0:
            raise ValueError("Invalid resize factors")
        self.queue = deque(maxlen=min_size)
        self.limit_max_size = max_size
        self.limit_min_size = min_size
        self._strategy = strategy or DynamicQueueResizeStrategy(
            shrink_timeout_seconds=15.0,
            shrink_check_interval_seconds=5.0,
            shrink_factor=shrink_factor,
        )
        self.growth_factor = growth_factor
        self.shrink_factor = shrink_factor
        self.process_batch_size = process_batch_size
        # includes put and pop operations. used to check if metrics update is needed
        self._operation_batch_counter = 0

        self._lock = Lock()
        self._metrics_lock = Lock()
        self.not_empty = Event()
        self.not_full = Event()
        self.should_stop = Event()
        # expand is only triggered by 'put', shrink depends on both size and elapsed time
        self._shrink_monitor = Thread(target=self._shrink_monitor_loop)
        self._metrics_monitor = Thread(target=self._metrics_monitor_loop)

        self.stats: Dict[str, int] = {
            "enqueued": 0,
            "dequeued": 0,
            "dropped": 0,
            "resize_count": 0,
        }

        self._metrics: Dict[str, Union[int, float]] = {
            "peak_queue_size": 0,
            "resize_frequency": 0.0,
            "total_processed_items": 0,
            "avg_load": 0.0,
        }

        self._start_time = time.time()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.name)

    # used for context manager
    def __enter__(self):
        self.start()
        return self

    # used for context manager
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __len__(self) -> int:
        with self._lock:
            return len(self.queue)

    def empty(self) -> bool:
        with self._lock:
            return len(self.queue) == 0

    def clear(self):
        with self._lock:
            self.queue.clear()

    @property
    def current_max_size(self) -> int:
        return self.queue.maxlen

    @property
    def name(self) -> str:
        return self._name

    def start(self):
        self.not_full.set()
        self._shrink_monitor.daemon = True
        self._metrics_monitor.daemon = True
        self._shrink_monitor.start()
        self._metrics_monitor.start()

    @property
    def is_running(self):
        return not self.should_stop.is_set()

    def enqueue(self, item: T) -> bool:
        # Tries to put an item in the queue, if the queue is full, it returns False
        try:
            with self._lock:
                if len(self.queue) >= self.queue.maxlen:
                    self.stats["dropped"] += 1
                    self.not_full.clear()
                    return False

                self.queue.append(item)
                self.stats["enqueued"] += 1
                self._operation_batch_counter += 1
                self.not_empty.set()
                len_after_put = len(self.queue)

            if self._strategy.should_expand(len_after_put, self.current_max_size):
                self._resize_queue(increase=True)
            return True
        except Exception as e:
            self.logger.error(f"Error in 'put': {e}, item: {item}")
            with self._lock:
                self.stats["dropped"] += 1
            return False

    def popleft(self) -> Optional[T]:
        with self._lock:
            if not self.queue:
                return None

            item = self.queue.popleft()
            self._operation_batch_counter += 1
            self.stats["dequeued"] += 1
        return item

    def peek(self) -> Optional[T]:
        with self._lock:
            if not self.queue:
                return None
            return self.queue[0]

    def get_metrics(self) -> Dict[str, float]:
        # Returns a copy of the metrics
        with self._metrics_lock:
            return self._metrics.copy()

    def get_stats(self) -> Dict[str, int]:
        # Returns a copy of the stats
        with self._lock:
            return self.stats.copy()

    def stop(self):
        self._handle_shutdown(None, None)

    def _shrink_monitor_loop(self):
        while not self.should_stop.is_set():
            with self._lock:
                queue_len = len(self.queue)
            should_shrink = self._strategy.should_shrink(queue_len)
            self.logger.info(f"{self.name}: Should shrink: {should_shrink}")
            if should_shrink:
                self._resize_queue(increase=False)
            # wait for a while before checking again to reduce overhead
            time.sleep(self._strategy.shrink_check_interval)

    def _metrics_monitor_loop(self):
        while not self.should_stop.is_set():
            self._update_metrics()
            time.sleep(2.0)

    def _resize_queue(self, increase: bool):
        self.logger.info(f"{'Expanding' if increase else 'Shrinking'} queue")
        with self._lock:
            current_max = self.current_max_size
        if increase:
            new_max = min(int(current_max * self.growth_factor), self.limit_max_size)
        else:
            new_max = max(int(current_max * self.shrink_factor), self.limit_min_size)
        self.logger.info(f"New max size: {new_max}, current max size: {current_max}")
        if new_max != current_max:
            with self._lock:
                new_queue = deque(self.queue, maxlen=new_max)
                self.queue = new_queue
                self.stats["resize_count"] += 1
            self.logger.info(
                f"Queue {'shrinked' if new_max < current_max else 'expanded'} from {current_max} to {new_max}"
            )

    def _handle_shutdown(self, signum, frame):
        self.logger.info("Shutting down the queue")
        self.should_stop.set()
        if hasattr(self, "_shrink_monitor") and self._shrink_monitor:
            if self._shrink_monitor.is_alive():
                self._shrink_monitor.join()
        if hasattr(self, "_metrics_monitor") and self._metrics_monitor:
            if self._metrics_monitor.is_alive():
                self._metrics_monitor.join()
        with self._lock:
            remaining = len(self.queue)
            self.queue.clear()
            if remaining > 0:
                self.logger.warning(f"Dropping {remaining} unprocessed items")

    def _update_metrics(self):
        with self._metrics_lock:
            with self._lock:
                if self._operation_batch_counter < self.process_batch_size:
                    return
                self._operation_batch_counter = 0
                current_size = len(self.queue)
                resize_count = self.stats["resize_count"]
            self._metrics["total_processed_items"] += self.process_batch_size
            self._metrics["peak_queue_size"] = max(
                self._metrics["peak_queue_size"], current_size
            )
            elapsed_time = time.time() - self._start_time
            self._metrics["resize_frequency"] = (
                resize_count / elapsed_time if elapsed_time > 0 else 0
            )
