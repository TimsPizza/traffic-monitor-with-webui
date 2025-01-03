import queue
from threading import Lock, Thread, Event
import logging
import time
from typing import Dict, Generic, List, Optional, TypeVar, Union
from utils.Interfaces import BaseDynamicQueueResizeStrategy
from utils.Strategy import DynamicQueueMetrics, DynamicQueueResizeStrategy

T = TypeVar("T")


class DynamicQueue(Generic[T]):
    def __init__(
        self,
        min_size: int = 1e3,
        max_size: int = 1e5,
        growth_factor: float = 1.5,
        shrink_factor: float = 0.5,
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

        self._strategy = strategy or DynamicQueueResizeStrategy(
            shrink_timeout_seconds=15.0,
            shrink_check_interval_seconds=5.0,
            shrink_factor=shrink_factor,
        )
        self.limit_max_size = int(max_size)
        self.limit_min_size = int(min_size)
        self.growth_factor = growth_factor
        self.shrink_factor = shrink_factor
        self.process_batch_size = process_batch_size
        self._queue = queue.Queue(maxsize=int(min_size))

        self._lock = Lock()
        self._metrics_lock = Lock()
        self.not_empty = Event()
        self.not_full = Event()
        self.should_stop = Event()
        self._shrink_monitor = None
        self._metrics_monitor = None
        self._metrics_update_interval = 5.0  # seconds
        self._avg_loads: List[float] = []
        self._metrics: DynamicQueueMetrics = DynamicQueueMetrics()
        self._start_time = time.time()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.name)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def name(self) -> str:
        return self._name

    def __len__(self) -> int:
        return self._queue.qsize()

    def empty(self) -> bool:
        return self._queue.empty()

    def clear(self):
        with self._lock:
            count = self._queue.qsize()
            while not self._queue.empty():
                self._queue.get_nowait()
            if count > 0:
                self.logger.debug(f"Cleared {count} items from the queue")

    @property
    def current_max_size(self) -> int:
        # Use the queue's maxsize as current max
        return self._queue.maxsize

    def start(self):
        self.not_full.set()
        self._shrink_monitor = Thread(target=self._shrink_monitor_loop, daemon=True)
        self._metrics_monitor = Thread(target=self._metrics_monitor_loop, daemon=True)
        self._shrink_monitor.start()
        self._metrics_monitor.start()

    def stop(self):
        self.logger.debug("Shutting down the queue")
        self.should_stop.set()
        if self._shrink_monitor and self._shrink_monitor.is_alive():
            self._shrink_monitor.join()
        if self._metrics_monitor and self._metrics_monitor.is_alive():
            self._metrics_monitor.join()
        self.clear()

    @property
    def is_running(self) -> bool:
        return not self.should_stop.is_set()

    def enqueue(self, item: T) -> bool:
        try:
            self._queue.put_nowait(item)
            with self._metrics_lock:
                self._metrics.enqueued += 1
            self.not_empty.set()
        except queue.Full:
            with self._metrics_lock:
                self._metrics.dropped += 1
            self.not_full.clear()
            return False

        # Check if we need to expand
        if self._strategy.should_expand(self._queue.qsize(), self.current_max_size):
            self._resize_queue(increase=True)
        return True

    def popleft(
        self, block: bool = False, timeout: Optional[float] = None
    ) -> Optional[T]:
        try:
            item = self._queue.get(block=block, timeout=timeout)
            with self._metrics_lock:
                self._metrics.dequeued += 1
            return item
        except queue.Empty:
            return None

    def peek(self) -> Optional[T]:
        # NOTE: This usage accesses the underlying queue list, which is not strictly safe,
        # but it's necessary to preserve "peek" functionality. Use with caution.
        with self._lock:
            if self._queue.empty():
                return None
            return self._queue.queue[0]

    def get_metrics(self) -> Dict[str, float]:
        with self._metrics_lock:
            return self._metrics.__dict__.copy()

    def _shrink_monitor_loop(self):
        while not self.should_stop.wait(self._strategy.shrink_check_interval):
            with self._lock:
                queue_len = self._queue.qsize()
            should_shrink = self._strategy.should_shrink(queue_len)
            self.logger.debug(f"{self.name}: Should shrink: {should_shrink}")
            if should_shrink:
                self._resize_queue(increase=False)

    def _metrics_monitor_loop(self):
        while not self.should_stop.wait(self._metrics_update_interval):
            self._update_metrics()

    def _resize_queue(self, increase: bool):
        self.logger.debug(f"{'Expanding' if increase else 'Shrinking'} queue")
        with self._lock:
            current_max = self._queue.maxsize
        if increase:
            new_max = min(int(current_max * self.growth_factor), self.limit_max_size)
        else:
            new_max = max(int(current_max * self.shrink_factor), self.limit_min_size)
        self.logger.debug(f"New max size: {new_max}, current max size: {current_max}")

        if new_max != current_max:
            with self._lock:
                self._queue.maxsize = new_max
                self._metrics.resize_count += 1
            self.logger.debug(
                f"Queue {'shrinked' if new_max < current_max else 'expanded'} "
                f"from {current_max} to {new_max}"
            )

    def _update_metrics(self):
        with self._metrics_lock:
            queue_len = self._queue.qsize()
            current_max = self._queue.maxsize
            resize_count = self._metrics.resize_count
            self._metrics.current_queue_max_size = current_max

            if len(self._avg_loads) > 60.0 // self._metrics_update_interval:
                self._avg_loads.pop(0)

            self._avg_loads.append(queue_len / current_max if current_max > 0 else 0)
            self._metrics.peak_queue_length = max(
                self._metrics.peak_queue_length, queue_len
            )
            elapsed_time = time.time() - self._start_time
            self._metrics.resize_frequency = (
                resize_count / elapsed_time if elapsed_time > 0 else 0
            )
            self._metrics.avg_load = (
                sum(self._avg_loads) / len(self._avg_loads)
                if len(self._avg_loads) > 0
                else 0
            )
