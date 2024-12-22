from typing import Dict, List, TypeVar, Generic, Optional, Union, Any
from threading import Thread, Lock, Event
import logging
import time

from .DynamicQueue import DynamicQueue
from .Interfaces import BufferStrategy, BatchProcessor, SizeBasedStrategy

T = TypeVar("T")


class DoubleBufferQueue(Generic[T]):
    def __init__(
        self,
        max_size: int = 10000,
        min_size: int = 1000,
        swap_strategy: Optional[BufferStrategy] = None,
        growth_factor: float = 1.5,
        shrink_factor: float = 0.5,
    ):
        # Initialize queues using DynamicQueue
        self._active_queue = DynamicQueue(
            min_size=min_size,
            max_size=max_size,
            growth_factor=growth_factor,
            shrink_factor=shrink_factor,
        )
        self._processing_queue = DynamicQueue(
            min_size=min_size,
            max_size=max_size,
            growth_factor=growth_factor,
            shrink_factor=shrink_factor,
        )

        self._strategy = swap_strategy or SizeBasedStrategy(threshold_ratio=0.5)
        self._processor: Optional[BatchProcessor[T]] = None

        # Threading controls
        self._lock = Lock()
        self._processing_lock = Lock()
        self._swap_event = Event()
        self._stop_event = Event()
        self._process_thread: Optional[Thread] = None

        # Metrics
        self._metrics: Dict[str, Union[int, float]] = {
            "total_processed": 0,
            "total_dropped": 0,
            "swap_count": 0,
            "last_swap_time": 0.0,
            "avg_process_time": 0.0,
            "total_process_time": 0.0,
        }

        self.logger = logging.getLogger("DoubleBufferQueue")

    def set_processor(self, processor: BatchProcessor[T]) -> None:
        """Set the batch processor"""
        self._processor = processor

    def start(self) -> None:
        """Start the processing thread"""
        if not self._processor:
            raise ValueError("Processor not set")

        self._process_thread = Thread(target=self._process_loop)
        self._process_thread.daemon = True
        self._active_queue.start()
        self._processing_queue.start()

        self._process_thread.start()

    def stop(self) -> None:
        """Stop processing and clean up resources"""
        self._stop_event.set()
        self._swap_event.set()  # Wake up processing thread

        if self._process_thread:
            self._process_thread.join(timeout=5.0)

        self._active_queue.stop()
        self._processing_queue.stop()

    def put(self, item: T) -> bool:
        """Add item to active queue"""
        with self._lock:
            success = self._active_queue.put(item)
            if not success:
                self._metrics["total_dropped"] += 1
                return False

            if self._should_swap():
                self._swap_event.set()
            return True

    def _should_swap(self) -> bool:
        """Check if buffers should be swapped"""
        return self._strategy.should_swap(
            self._active_queue.size, self._active_queue.max_size
        )

    def _swap_buffers(self) -> None:
        """Swap active and processing queues"""
        with self._lock, self._processing_lock:
            self._active_queue, self._processing_queue = (
                self._processing_queue,
                self._active_queue,
            )
            self._metrics["swap_count"] += 1
            self._metrics["last_swap_time"] = time.time()

            if self._strategy:
                self._strategy.on_swap()

    def _process_items(self, items: List[T]) -> None:
        """Process a batch of items"""
        if not items:
            return

        try:
            start_time = time.time()
            # TODO: consider calling process_batch directly when batch has not been filled for a long time
            self._processor.process_batch(items)
            process_time = time.time() - start_time

            with self._lock:
                self._metrics["total_processed"] += len(items)
                self._metrics["total_process_time"] += process_time
                self._metrics["avg_process_time"] = (
                    self._metrics["total_process_time"]
                    / self._metrics["total_processed"]
                )
        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")

    def _process_loop(self) -> None:
        """Main processing loop"""
        while not self._stop_event.is_set():
            if self._swap_event.wait(timeout=0.1):
                self._swap_buffers()
                self._swap_event.clear()

    @property
    def metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self._lock:
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
