import logging
from statistics import mean
from threading import Event
import time
from typing import List
from anyio import Lock
from scapy.all import Ether

from packet.Packet import CapturedPacket
from utils.DoubleBufferQueue import DoubleBufferQueue
from concurrent.futures import ThreadPoolExecutor

from utils.Interfaces import ConsumerMetrics


class PacketConsumer:
    def __init__(self, buffer, max_workers=4, batch_size=10):
        self._buffer: DoubleBufferQueue = buffer
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._min_batch_size = max(1, batch_size // 2)
        self._max_batch_size = batch_size * 2
        self._current_batch_size = batch_size
        self._max_wait_time = 0.1  # 100ms
        self._stop_event = Event()
        self._metrics_lock = Lock()
        
        # 性能指标
        self._metrics = ConsumerMetrics()
        self._batch_sizes = []
        self._wait_times = []
        self._processing_times = []
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # 监控间隔
        self._metrics_interval = 5  # 5秒
        self._last_metrics_time = time.time()

    def start(self):
        self._stop_event.clear()
        self.executor.submit(self._consume_loop)
        self.executor.submit(self._monitor_metrics)
        self.logger.info("PacketConsumer started")

    def stop(self):
        self._stop_event.set()
        self.executor.shutdown(wait=True)
        self.logger.info("PacketConsumer stopped")
        self._log_final_metrics()

    def _consume_loop(self):
        while not self._stop_event.is_set():
            start_wait = time.time()
            batch = self._read_batch_from_queue(self._current_batch_size)
            wait_time = time.time() - start_wait
            
            if batch:
                self._update_wait_metrics(wait_time)
                self._process_batch(batch)
                self._adjust_batch_size(wait_time, len(batch))

    def _read_batch_from_queue(self, batch_size) -> List[CapturedPacket]:
        """batch read with timeout support"""
        batch = []
        start_time = time.time()
        
        while len(batch) < batch_size and (time.time() - start_time) < self._max_wait_time:
            packet = self._buffer.popleft()
            if packet:
                batch.append(packet)
            elif len(batch) >= self._min_batch_size:
                break
            elif self._stop_event.is_set():
                break
                
        return batch

    def _process_batch(self, batch: List[CapturedPacket]):
        start_time = time.time()
        futures = []
        
        for packet in batch:
            if self._should_accept_more_tasks():
                futures.append(self.executor.submit(self._process_packet, packet))
            else:
                self.logger.warning("Thread pool saturated, implementing backpressure")
                break
                
        # waiting for all tasks are done
        for future in futures:
            try:
                future.result()
                
            except Exception as e:
                self.logger.error(f"Error processing packet: {e}")
                
        self._update_processing_metrics(time.time() - start_time, len(batch))

    def _process_packet(self, packet):
        """单个数据包处理"""
        try:
            scapy_packet = Ether(packet)
            # simulate packet processing 
            print(f"Processed packet: {scapy_packet.summary()}")
        except Exception as e:
            self.logger.error(f"Error in packet processing: {e}")
            raise

    def _should_accept_more_tasks(self) -> bool:
        """检查线程池负载情况"""
        # 获取线程池当前状态
        pool = self.executor._pool
        if pool:
            active_threads = len([t for t in pool if t.is_alive()])
            return active_threads < self.executor._max_workers
        return True

    def _adjust_batch_size(self, wait_time: float, actual_batch_size: int):
        """动态调整批处理大小"""
        if wait_time < self._max_wait_time * 0.5 and actual_batch_size >= self._current_batch_size:
            # 队列负载高，增加批量
            self._current_batch_size = min(self._current_batch_size * 1.5, self._max_batch_size)
        elif wait_time >= self._max_wait_time or actual_batch_size < self._min_batch_size:
            # 队列负载低，减少批量
            self._current_batch_size = max(self._current_batch_size * 0.8, self._min_batch_size)

    def _update_wait_metrics(self, wait_time: float):
        """更新等待时间指标"""
        with self._metrics_lock:
            self._wait_times.append(wait_time)
            if len(self._wait_times) > 100:
                self._wait_times.pop(0)
            self._metrics.avg_wait_time = mean(self._wait_times)

    def _update_processing_metrics(self, processing_time: float, batch_size: int):
        """更新处理时间和批量大小指标"""
        with self._metrics_lock:
            self._processing_times.append(processing_time)
            self._batch_sizes.append(batch_size)
            if len(self._processing_times) > 100:
                self._processing_times.pop(0)
            if len(self._batch_sizes) > 100:
                self._batch_sizes.pop(0)
            
            self._metrics.processing_delay = mean(self._processing_times)
            self._metrics.avg_batch_size = mean(self._batch_sizes)
            self._metrics.processed_packets += batch_size

    def _monitor_metrics(self):
        """定期监控和记录性能指标"""
        while not self._stop_event.is_set():
            current_time = time.time()
            if current_time - self._last_metrics_time >= self._metrics_interval:
                self._log_metrics()
                self._last_metrics_time = current_time
            time.sleep(1)

    def _log_metrics(self):
        """记录性能指标"""
        with self._metrics_lock:
            self.logger.info(
                f"Consumer Metrics - "
                f"Avg Batch Size: {self._metrics.avg_batch_size:.2f}, "
                f"Avg Wait Time: {self._metrics.avg_wait_time*1000:.2f}ms, "
                f"Processing Delay: {self._metrics.processing_delay*1000:.2f}ms, "
                f"Processed Packets: {self._metrics.processed_packets}, "
                f"Current Batch Size: {self._current_batch_size}"
            )

    def _log_final_metrics(self):
        """记录最终的性能统计"""
        with self._metrics_lock:
            self.logger.info(
                f"Final Consumer Metrics - "
                f"Total Processed: {self._metrics.processed_packets}, "
                f"Avg Batch Size: {self._metrics.avg_batch_size:.2f}, "
                f"Avg Processing Delay: {self._metrics.processing_delay*1000:.2f}ms"
            )