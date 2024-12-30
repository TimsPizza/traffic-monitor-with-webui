from asyncio import futures
import logging
from statistics import mean
from threading import Event, Lock
import time
from typing import List
from scapy.all import Ether

from packet.Packet import CapturedPacket
from utils import DoubleBufferQueue
from concurrent.futures import Future, ThreadPoolExecutor

from utils import ConsumerMetrics


class PacketConsumer:
    def __init__(self, buffer, max_workers=4, batch_size=256):
        if not buffer or not isinstance(buffer, DoubleBufferQueue):
            raise ValueError("Invalid buffer provided")
        if max_workers < 1:
            raise ValueError("Invalid max_workers value")
        if batch_size < 1:
            raise ValueError("Invalid batch_size value")
        self._buffer: DoubleBufferQueue = buffer
        self._max_workers = max_workers
        self.executor: ThreadPoolExecutor = None
        self._min_batch_size = max(1, batch_size // 2)
        self._max_batch_size = batch_size * 4
        self._current_batch_size = batch_size
        self._max_wait_time = 5  # max wait time for collecting a batch from the buffer
        self._stop_event = Event()
        self._stop_event.set()
        self._lock = Lock()
        self._pending_tasks = 0
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
        self.executor = ThreadPoolExecutor(max_workers=self._max_workers)
        self.logger.info("PacketConsumer started")
        self.executor.submit(self._consume_loop)
        self.executor.submit(self._monitor_metrics)

    @property
    def is_running(self):
        return not self._stop_event.is_set()

    def stop(self):
        self._stop_event.set()
        self.executor.shutdown(wait=True)
        self.logger.info("PacketConsumer stopped")
        self._log_final_metrics()
        self.logger.info("Consumer stopped")

    def _submit_task(self, func, *args, **kwargs):
        """对外提交任务的方法"""
        with self._lock:
            self._pending_tasks += 1

        future = self.executor.submit(func, *args, **kwargs)
        future.add_done_callback(self._on_task_done)
        return future

    def _on_task_done(self, future: Future):
        """任务完成回调，减少进行中的任务数"""
        with self._lock:
            self._pending_tasks -= 1

    def _consume_loop(self):
        while not self._stop_event.is_set():
            start_wait = time.time()
            batch = self._read_batch_from_queue(self._current_batch_size)
            wait_time = time.time() - start_wait
            self.logger.info(
                f"Read batch of {len(batch)} packets in {wait_time:.2f} seconds"
            )
            if batch:
                self._update_wait_metrics(wait_time)
                self._process_batch(batch)
                self._adjust_batch_size(wait_time, len(batch))
            self._stop_event.wait(0.05)

    def _read_batch_from_queue(self, batch_size) -> List[CapturedPacket]:
        """batch read with timeout support"""
        batch = []
        start_time = time.time()
        while (
            len(batch) < batch_size and (time.time() - start_time) < self._max_wait_time
        ):
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
        task_future = None
        try:
            if self._should_accept_more_tasks():
                task_future = self._submit_task(self._process_batch_executor, batch)
                self.logger.info(
                    f"Submitted batch of {len(batch)} packets for processing"
                )
            else:
                self.logger.warning("Thread pool saturated, implementing backpressure")

            if task_future:
                task_future.result()
            # self._update_processing_metrics(time.time() - start_time, len(batch))
        except Exception as e:
            self.logger.error(f"Error batch processing packet: {e}")

    def _process_batch_executor(self, batch: List[CapturedPacket]):
        if not batch:
            return
        start_time = time.time()
        for packet in batch:
            self._process_packet(packet)
        self._update_processing_metrics(time.time() - start_time, len(batch))

    def _process_packet(self, packet: CapturedPacket):
        """单个数据包处理"""
        time_stamp, packet = packet.timestamp, packet.packet
        try:
            scapy_packet = Ether(packet)
            # simulate packet processing, delay 1ms
            # print(f"Processed packet: {scapy_packet.summary()}")
            time.sleep(0.001)
        except Exception as e:
            self.logger.error(f"Error in packet processing: {e}")
            raise

    def _should_accept_more_tasks(self) -> bool:
        """检查当前进行中的任务数量是否小于最大工作线程数"""
        with self._lock:
            return self._pending_tasks < self._max_workers

    def _adjust_batch_size(self, wait_time: float, actual_batch_size: int):
        """动态调整批处理大小"""
        if (
            wait_time < self._max_wait_time * 0.5
            and actual_batch_size >= self._current_batch_size
        ):
            # 队列负载高，增加批量
            self._current_batch_size = min(
                self._current_batch_size * 1.5, self._max_batch_size
            )
        elif (
            wait_time >= self._max_wait_time or actual_batch_size < self._min_batch_size
        ):
            # 队列负载低，减少批量
            self._current_batch_size = max(
                self._current_batch_size * 0.8, self._min_batch_size
            )

    def _update_wait_metrics(self, wait_time: float):
        """更新等待时间指标"""
        self.logger.info(f"Updating wait metrics, wait time: {wait_time:.2f} seconds")
        try:
            with self._metrics_lock:
                self._wait_times.append(wait_time)
                if len(self._wait_times) > 100:
                    self._wait_times.pop(0)
                self._metrics.avg_wait_time = mean(self._wait_times)
        except Exception as e:
            self.logger.error(f"Error updating wait metrics: {e}")
        self.logger.info(
            f"Updated wait metrics, avg wait time: {self._metrics.avg_wait_time:.2f} seconds"
        )

    def _update_processing_metrics(self, processing_time: float, batch_size: int):
        """更新处理时间和批量大小指标"""
        self.logger.info(
            f"Updating processing metrics, processing time: {processing_time:.2f} seconds, batch size: {batch_size}"
        )
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
        self.logger.info(
            f"Updated processing metrics, avg processing delay: {self._metrics.processing_delay:.2f} seconds, "
            f"avg batch size: {self._metrics.avg_batch_size:.2f}, processed packets: {self._metrics.processed_packets}"
        )

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
