from typing import Callable, Optional
import netifaces
import pcap
from threading import Thread, Event
import logging


class PacketCapturer:
    def __init__(self, interface: str, filter: Optional[str] = None):
        self.interface = interface
        if self.interface not in netifaces.interfaces():
            raise ValueError(f"Interface {self.interface} does not exist")

        self._pcap = pcap.pcap(name=interface, promisc=True, immediate=True)
        if filter:
            self.set_filter(filter)
        self._stop_event = Event()
        self._capture_thread: Optional[Thread] = Thread(target=self._capture_loop)
        self._callback: Optional[Callable] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def set_filter(self, filter: str) -> None:
        """Set packet filter"""
        self._pcap.setfilter(filter)
        self.logger.info(f"Filter set to: {filter}")

    def register_callback(self, callback: Callable[[bytes, float], None]) -> None:
        """Register callback for packet processing"""
        self._callback = callback
        self.logger.info(f"Callback registered:{callback}")

    def start_capture(self) -> None:
        """Start packet capture in separate thread"""
        if self._capture_thread is not None:
            return
        
        self._capture_thread.daemon = True
        self._capture_thread.start()
        self.logger.info(
            "Capture started with filter: {self._pcap.filter}, listening on interface: {self.interface}"
        )

    def stop_capture(self) -> None:
        """Stop packet capture"""
        self._stop_event.set()
        if self._capture_thread:
            self._capture_thread.join(timeout=5.0)
        self._pcap.close()

    def _capture_loop(self) -> None:
        """Main capture loop"""
        try:
            while not self._stop_event.is_set():
                for timestamp, packet in self._pcap:
                    if self._stop_event.is_set():
                        break
                    if self._callback:
                        try:
                            self._callback(packet, timestamp)
                        except Exception as e:
                            self.logger.error(f"Error in packet producer callback: {e}")
        except Exception as e:
            self.logger.error(f"Capture error: {e}")

    def __enter__(self):
        self.start_capture()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_capture()
