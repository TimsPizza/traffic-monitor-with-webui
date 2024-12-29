import logging
import time
from typing import Optional
from packet.Packet import CapturedPacket
from packet.PacketCapturer import PacketCapturer
from utils.DoubleBufferQueue import DoubleBufferQueue
from scapy.all import Ether


class PacketProducer:
    def __init__(
        self,
        buffer: DoubleBufferQueue = None,
        filter: str = None,
        interface: str = None,
    ):
        self._buffer = buffer
        if self._buffer is None:
            raise ValueError("Buffer cannot be None")
        self._filter = filter
        self.captured_packets_count = 0
        self._capturer = PacketCapturer(interface=interface, filter=filter)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def start(self):
        self._capturer.register_callback(self._on_packet_captured)
        self._capturer.start()
        self.logger.info(f"Producer started at {time.time()}")

    @property
    def is_running(self):
        return self._capturer.is_running

    def stop(self):
        self._capturer.stop()
        self.logger.info(f"Producer stopped at {time.time()}")

    def restart(self):
        self._capturer.stop()
        time.sleep(0.5)
        self._capturer.start()
        self.logger.info(f"Producer restarted at {time.time()}")

    def apply_filter(self, filter):
        # TODO: implement filter interface?
        self._capturer.set_filter(filter)

    def _on_packet_captured(self, packet: bytes, timestamp: float):
        self.captured_packets_count += 1
        # push raw packet to avoid unnecessary parsing leading to data loss
        self._enqueue_packet(CapturedPacket(packet, timestamp))
        # self.logger.info(
        #     f"{self.captured_packets_count}th Packet: {scapy_packet.summary()} captured at {timestamp}, "
        #     f"Protocol: {scapy_packet.proto if hasattr(scapy_packet, 'proto') else 'N/A'}, "
        #     f"Source: {scapy_packet.src if hasattr(scapy_packet, 'src') else 'N/A'}, "
        #     f"Destination Port: {scapy_packet.dport if hasattr(scapy_packet, 'dport') else 'N/A'}"
        # )

    def _enqueue_packet(self, packet):
        self._buffer.enqueue(packet)
