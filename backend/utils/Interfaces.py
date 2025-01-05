from abc import ABC, abstractmethod
from dataclasses import dataclass
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
    
@dataclass
class ConsumerMetrics:
    avg_batch_size: float = 0
    avg_wait_time: float = 0
    processing_delay: float = 0
    processed_packets: int = 0
    packet_size_sum: int = 0


@dataclass
class ProducerMetrics:
    total_dropped: int = 0
    total_processed: int = 0
    swap_count: int = 0
    last_swap_time: float = 0.0
    avg_process_time: float = 0.0
    total_process_time: float = 0.0


@dataclass
class DynamicQueueMetrics:
    enqueued: int = 0
    dequeued: int = 0
    dropped: int = 0.0
    resize_count: int = 0.0
    peak_queue_length: int = 0.0
    current_queue_max_size: int = 0.0
    resize_frequency: float = 0.0
    avg_load: float = 0.0


