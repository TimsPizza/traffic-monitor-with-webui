from threading import Event
from packet import PacketConsumer, PacketProducer, CapturedPacket
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
