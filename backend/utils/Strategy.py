from abc import ABC, abstractmethod
from dataclasses import dataclass
import time

from utils.Interfaces import BaseDynamicQueueResizeStrategy, BufferStrategy


class TimeBasedStrategy(BufferStrategy):
    """Based on time interval"""

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
    
class MixedSwapStrategy(BufferStrategy):
    """Based on both time interval and size of the queue"""

    def __init__(self, swap_interval_sec: float, threshold_ratio: float):
        self.time_based_strategy = TimeBasedStrategy(swap_interval_sec)
        self.size_based_strategy = SizeBasedStrategy(threshold_ratio)

    def should_swap(self, current_size: int, max_size: int) -> bool:
        return (
            self.time_based_strategy.should_swap()
            or self.size_based_strategy.should_swap(current_size, max_size)
        )

    def on_swap(self):
        self.time_based_strategy.on_swap()
        self.size_based_strategy.on_swap()


class DynamicQueueResizeStrategy(BaseDynamicQueueResizeStrategy):
    def __init__(
        self,
        expand_threshold_ratio: float = 0.8,
        shrink_factor: float = None,
        shrink_threshold_ratio: float = 0.6,
        shrink_timeout_seconds: float = 30.0,
        shrink_check_interval_seconds: float = 5.0,
    ):
        if not 0 < expand_threshold_ratio < 1:
            raise ValueError("Threshold ratio must be between 0 and 1")
        if shrink_threshold_ratio > expand_threshold_ratio:
            raise ValueError(
                "Shrink threshold ratio must be less than expand threshold ratio to avoid repeated expansion just after shrink"
            )
        self.expand_threshold_ratio = expand_threshold_ratio
        self.shrink_threshold_ratio = shrink_threshold_ratio
        self.shrink_factor = shrink_factor
        self.shrink_timeout = shrink_timeout_seconds
        self.shrink_check_interval = shrink_check_interval_seconds
        self.last_expand_time = time.time()
        self.last_shrink_time = time.time()

    def should_expand(self, current_size: int, max_size: int) -> bool:
        flag = current_size >= (max_size * self.expand_threshold_ratio)
        # print(f"current_size: {current_size}, max_size: {max_size}, flag: {flag}")
        if flag:
            self.on_expand()
        return flag

    def should_shrink(self, current_size: int) -> bool:
        if not self.shrink_factor:
            raise ValueError("Shrink factor must be specified to use shrink strategy")
        time_now = time.time()
        flag_time = time_now - self.last_expand_time >= self.shrink_timeout
        max_size_after_shrink = current_size * self.shrink_factor
        flag_size = current_size <= (
            max_size_after_shrink * self.shrink_threshold_ratio
        )

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

