from threading import Event

from core.config import ENV_CONFIG
from .Processors import (
    check_application_protocol,
    check_src_ip_region,
    check_ssh_type,
    check_tcp,
    check_udp,
)
from packet.PacketConsumer import PacketConsumer
from packet.PacketProducer import PacketProducer
from packet.Packet import CapturedPacket
from utils import DoubleBufferQueue


class PacketAnalyzer:
    def __init__(
        self,
        buffer_min_size: int = 256,
        buffer_max_size: int = 8192,
        buffer_growth_factor: float = 1.5,
        buffer_shrink_factor: float = 0.5,
        capture_interface: str = None,
        capture_filter: str = None,
        consumer_max_workers: int = 4,
        consumer_batch_size: int = 256,
    ):
        self._stop_event = Event()
        self._stop_event.set()
        self._double_buffer_queue: DoubleBufferQueue = DoubleBufferQueue[
            CapturedPacket
        ](
            min_size=buffer_min_size,
            max_size=buffer_max_size,
            growth_factor=buffer_growth_factor,
            shrink_factor=buffer_shrink_factor,
        )
        self._packet_producer: PacketProducer = PacketProducer(
            self._double_buffer_queue,
            interface=capture_interface,
            filter=capture_filter,
        )
        self._packet_consumer: PacketConsumer = PacketConsumer(
            self._double_buffer_queue,
            max_workers=consumer_max_workers,
            batch_size=consumer_batch_size,
        )
        self._packet_consumer.add_processor(check_udp)
        self._packet_consumer.add_processor(check_tcp)
        self._packet_consumer.add_processor(check_application_protocol)
        self._packet_consumer.add_processor(check_ssh_type)
        self._packet_consumer.add_processor(check_src_ip_region)

    def start(self):
        self._stop_event.clear()
        self._double_buffer_queue.start()
        self._packet_consumer.start()
        self._packet_producer.start()

    @property
    def is_running(self):
        return (
            not self._stop_event.is_set()
            or self._double_buffer_queue.is_running
            or self._packet_consumer.is_running
            or self._packet_producer.is_running
        )

    def stop(self):
        self._stop_event.set()
        self._packet_producer.stop()
        self._packet_consumer.stop()
        self._double_buffer_queue.stop()


class AnalyzerSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PacketAnalyzer(
                buffer_min_size=ENV_CONFIG.queue_min_size,
                buffer_max_size=ENV_CONFIG.queue_max_size,
                consumer_max_workers=ENV_CONFIG.max_workers,
                consumer_batch_size=ENV_CONFIG.consumer_batch_size,
                capture_interface=ENV_CONFIG.capture_interface,
            )
        return cls._instance
