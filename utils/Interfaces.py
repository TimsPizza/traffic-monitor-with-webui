from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Optional, TYPE_CHECKING
from threading import Thread, Event
import time
import logging

if TYPE_CHECKING:
    from .DynamicQueue import DynamicQueue
    from .DoubleBufferQueue import DoubleBufferQueue

T = TypeVar("T")


class BaseBatchConsumer(Generic[T]):
    """批处理器接口"""

    @abstractmethod
    def process_batch(self, items: List[T]) -> None:
        """处理一批数据"""
        pass


class DataProcessor(BaseBatchConsumer[T]):
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
    """Based on the size of the queue"""

    def __init__(self, threshold_ratio: float):
        # use ratio instead of absolute size
        if not 0 < threshold_ratio < 1:
            raise ValueError("Threshold ratio must be between 0 and 1")
        self.threshold_ratio = threshold_ratio

    def should_swap(self, current_size: int, max_size: int) -> bool:
        # swap when current size exceeds the threshold
        return current_size >= (max_size * self.threshold_ratio)

    def on_swap(self):
        pass


class BaseDynamicQueueResizeStrategy(ABC):
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


class DynamicQueueResizeStrategy(BaseDynamicQueueResizeStrategy):
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
        flag_time = time.time() - self.last_expand_time >= self.shrink_timeout
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
