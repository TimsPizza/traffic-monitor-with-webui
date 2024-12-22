from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Optional, TYPE_CHECKING
from threading import Thread, Event
import time
import logging

if TYPE_CHECKING:
    from .DynamicQueue import DynamicQueue
    from .DoubleBufferQueue import DoubleBufferQueue

T = TypeVar("T")


class BatchProcessor(Generic[T]):
    """批处理器接口"""

    @abstractmethod
    def process_batch(self, items: List[T]) -> None:
        """处理一批数据"""
        pass


class DataProcessor(BatchProcessor[T]):
    """数据处理器基类"""

    def __init__(self, queue: "DoubleBufferQueue[T]"):
        self.queue = queue
        self.queue.processor = self.process_batch

    @abstractmethod
    def process_batch(self, items: List[T]) -> None:
        """处理一批数据的具体实现"""
        pass

    def start(self) -> None:
        """启动处理"""
        self.queue.start()

    def stop(self) -> None:
        """停止处理"""
        self.queue.stop()


class Producer(Generic[T], ABC):
    """Base producer interface"""

    def __init__(self, queue: DoubleBufferQueue[T]):
        self.queue = queue
        self._should_stop = Event()
        self._producer_thread: Optional[Thread] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def produce(self) -> Optional[T]:
        """Generate next item to be produced"""
        pass

    def start(self) -> None:
        """Start the producer thread"""
        self._producer_thread = Thread(target=self._produce_loop, daemon=True)
        self._producer_thread.start()

    def stop(self) -> None:
        """Stop the producer thread"""
        self._should_stop.set()
        if self._producer_thread and self._producer_thread.is_alive():
            self._producer_thread.join(timeout=5.0)

    def _produce_loop(self) -> None:
        """Main production loop"""
        while not self._should_stop.is_set():
            try:
                item = self.produce()
                if item is not None:
                    if not self.queue.put(item):
                        self.logger.warning("Queue full, item dropped")
            except Exception as e:
                self.logger.error(f"Error in production loop: {e}")


class BatchProducer(Producer[T]):
    """Base class for batch-oriented producers"""

    def __init__(
        self,
        queue: DoubleBufferQueue[T],
        batch_size: int = 100,
        produce_interval: float = 0.1,
    ):
        super().__init__(queue)
        self.batch_size = batch_size
        self.produce_interval = produce_interval
        self._items_produced = 0
        self._last_produce_time = time.time()

    @abstractmethod
    def produce_batch(self) -> list[T]:
        """Generate a batch of items"""
        pass

    def produce(self) -> Optional[T]:
        """Implement single item production from batch"""
        current_time = time.time()
        if current_time - self._last_produce_time < self.produce_interval:
            time.sleep(self.produce_interval)

        batch = self.produce_batch()
        self._last_produce_time = time.time()
        self._items_produced += len(batch)

        for item in batch:
            if self._should_stop.is_set():
                break
            if not self.queue.put(item):
                self.logger.warning("Queue full, dropping remaining batch items")
                break


class BufferStrategy(ABC):
    """缓冲区策略抽象基类"""

    @abstractmethod
    def should_swap(self) -> bool:
        """决定是否应该交换缓冲区"""
        pass

    @abstractmethod
    def on_swap(self) -> None:
        """缓冲区交换时的回调"""
        pass


class TimeBasedStrategy(BufferStrategy):
    """基于时间的缓冲区交换策略"""

    def __init__(self, interval: float):
        self.interval = interval
        self.last_swap = time.time()

    def should_swap(self) -> bool:
        return time.time() - self.last_swap >= self.interval

    def on_swap(self) -> None:
        self.last_swap = time.time()


class SizeBasedStrategy(BufferStrategy):
    """基于当前队列大小的交换策略"""

    def __init__(self, threshold_ratio: float):
        # 使用比例而不是固定大小
        if not 0 < threshold_ratio < 1:
            raise ValueError("Threshold ratio must be between 0 and 1")
        self.threshold_ratio = threshold_ratio

    def should_swap(self, current_size: int, max_size: int) -> bool:
        # 基于当前队列大小和其容量的比例来决定是否交换
        return current_size >= (max_size * self.threshold_ratio)


class DynamicQueueResizeStrategyBase(ABC):
    @abstractmethod
    def should_expand(self, current_size: int, max_size: int) -> bool:
        pass

    @abstractmethod
    def should_shrink(self, current_size: int, max_size: int) -> bool:
        pass

    @abstractmethod
    def on_expand(self) -> None:
        pass

    @abstractmethod
    def on_shrink(self) -> None:
        pass


class DynamicQueueResizeStrategy(DynamicQueueResizeStrategyBase):
    def __init__(
        self,
        expand_threshold_ratio: float,
        shrink_timeout_seconds: float = 30.0,
        shrink_check_interval_seconds: float = 5.0,
    ):
        if not 0 < expand_threshold_ratio < 1:
            raise ValueError("Threshold ratio must be between 0 and 1")
        self.expand_threshold_ratio = expand_threshold_ratio
        self.shrink_timeout = shrink_timeout_seconds
        self.shrink_check_interval = shrink_check_interval_seconds
        self.last_expand_time = time.time()
        self.last_shrink_time = time.time()

    def should_expand(self, current_size: int, max_size: int) -> bool:
        flag = current_size >= (max_size * self.expand_threshold_ratio)
        if flag:
            self.on_expand()
        return flag

    def should_shrink(self, current_size: int, max_size: int) -> bool:
        flag_time = time.time() - self.last_shrink_time >= self.shrink_timeout
        flag_size = not self.should_expand(current_size, max_size)
        if flag_time and flag_size:
            self.on_shrink()
        return flag_time and flag_size

    def on_expand(self) -> None:
        self.last_expand_time = time.time()

    def on_shrink(self) -> None:
        self.last_shrink_time = time.time()

    def __str__(self):
        return (
            super().__str__()
            + f"expand_threshold_ratio: {self.expand_threshold_ratio}, shrink_timeout: {self.shrink_timeout}"
        )
