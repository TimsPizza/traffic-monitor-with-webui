from typing import Dict, List, TypeVar, Generic, Optional, Union, Any, Tuple
from threading import Thread, Lock, Event
import logging
import time
from threading import RLock
import threading

from .DynamicQueue import DynamicQueue
from utils.Interfaces import BaseBatchConsumer, BufferStrategy, SizeBasedStrategy

T = TypeVar("T")


class DoubleBufferQueue(Generic[T]):
    def __init__(
        self,
        max_size: int = 32768,
        min_size: int = 256,
        swap_strategy: Optional[BufferStrategy] = None,
        growth_factor: float = 1.5,
        shrink_factor: float = 0.5,
    ):
        # Initialize queues using DynamicQueue in an immutable tuple
        self._queues: Tuple[DynamicQueue, DynamicQueue] = (
            DynamicQueue(
                min_size=min_size,
                max_size=max_size,
                growth_factor=growth_factor,
                shrink_factor=shrink_factor,
                queue_id="1",
            ),
            DynamicQueue(
                min_size=min_size,
                max_size=max_size,
                growth_factor=growth_factor,
                shrink_factor=shrink_factor,
                queue_id="2",
            ),
        )
        self.max_size = max_size
        self.min_size = min_size
        self._active_index = 0
        self._index_lock = Lock()
        # make sure threshold_ratio is less than Dynamic queue expand_threshold_ratio because it is designed to be expanded first, or error will occur
        self._strategy = swap_strategy or SizeBasedStrategy(threshold_ratio=0.8)

        # Threading controls
        self._metrics_lock = RLock()  # For metrics updates
        self._swap_event = Event()
        self._stop_event = Event()
        self._swap_thread = Thread(target=self._swap_monitor_by_time_loop)
        # Metrics
        self._metrics: Dict[str, Union[int, float]] = {
            "total_processed": 0,
            "total_dropped": 0,
            "swap_count": 0,
            "last_swap_time": 0.0,
            "avg_process_time": 0.0,
            "total_process_time": 0.0,
        }

        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def _active_queue(self) -> DynamicQueue:
        return self._queues[self._active_index]

    @property
    def _processing_queue(self) -> DynamicQueue:
        return self._queues[1 - self._active_index]

    def enqueue(self, item: T) -> bool:
        """Add item to active queue"""
        success = self._active_queue.enqueue(item)

        if not success:
            with self._metrics_lock:
                self._metrics["total_dropped"] += 1
            return False

        if self._strategy and self._strategy.should_swap(
            current_size=len(self._active_queue),
            max_size=self._active_queue.current_max_size,
        ):
            # self._swap_event.set()
            self.logger.info("Swap event triggered")
            self._swap_buffers()
        return True

    def popleft(self) -> Optional[T]:
        """Pop item from processing queue"""
        if not self._processing_queue.empty():
            item = self._processing_queue.popleft()
        else:
            # dynamic queue expand first, this is to prevent consumer from waiting on the empty processing-queue
            item = self._active_queue.popleft()
            if item:
                with self._metrics_lock:
                    self._metrics["total_processed"] += 1
        return item

    def _swap_monitor_by_time_loop(self) -> None:
        while not self._stop_event.is_set():
            self.logger.info("Waiting for swap event")
            self._swap_event.wait()
            self._swap_buffers()
            self._swap_event.clear()

    def _swap_buffers(self) -> None:
        """Swap active and processing queues using atomic index swap"""
        with self._index_lock:
            self._active_index = 1 - self._active_index

        with self._metrics_lock:
            self._metrics["swap_count"] += 1
            self._metrics["last_swap_time"] = time.time()

        if self._strategy:
            self._strategy.on_swap()
        self.logger.info("Swapped queues")

    def start(self) -> None:
        """Start processing"""
        self._swap_thread.start()
        self._queues[0].start()
        self._queues[1].start()

    def stop(self) -> None:
        """Stop processing and clean up resources"""
        self._stop_event.set()
        self._swap_event.set()

        self._queues[0].stop()
        self._queues[1].stop()
        self._swap_thread.join()

    @property
    def metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self._metrics_lock:
            return {
                **self._metrics,
                "active_queue_metrics": self._active_queue.get_metrics(),
                "processing_queue_metrics": self._processing_queue.get_metrics(),
            }

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
