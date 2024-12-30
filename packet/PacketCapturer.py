import time
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

        self._pcap = None
        self._batch_size = 128  # Process packets in small batches
        self._interface = interface
        self._stop_event = Event()
        self._stop_event.set()
        self._capture_thread: Thread = None
        self._callback: Optional[Callable] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        if filter:
            self._cache_filter(filter)

    def _cache_filter(self, filter: str) -> None:
        """Cache packet filter before pcap object is initialized"""
        self._filter = filter
        self.logger.info(f"Filter cached: {filter}")

    def set_filter(self, filter: str) -> None:
        """Set packet filter"""
        if self._stop_event.is_set():
            self._cache_filter(filter)
            self.logger.info(f"Filter cached: {filter}")
            return
        self._pcap.setfilter(filter)
        self.logger.info(f"Filter set to: {filter}")

    def register_callback(self, callback: Callable[[bytes, float], None]) -> None:
        """Register callback for packet processing"""
        self._callback = callback
        self.logger.info(f"Callback registered:{callback}")

    def start(self) -> None:
        """Start packet capture in separate thread"""
        self._stop_event.clear()
        self._pcap = pcap.pcap(name=self._interface, promisc=True, immediate=True)
        self._pcap.setnonblock(True)
        if self._filter:
            self.set_filter(self._filter)
            self.logger.info(f"Using cached filter: {self._filter}")
            
        self._capture_thread = Thread(target=self._capture_loop)
        self._capture_thread.start()
        self.logger.info(
            f"Capture started with filter: {self._pcap.filter}, listening on interface: {self.interface}"
        )

    @property
    def is_running(self):
        return not self._stop_event.is_set()

    def stop(self) -> None:
        """Stop packet capture"""
        self._stop_event.set()
        self._pcap.close() if self._pcap else None
        self.logger.info(f"Capture stopped at {time.time()}")

    def _capture_loop(self) -> None:
        """Non-blocking capture loop with batched processing"""
        if not self._pcap:
            raise ValueError("Pcap object not initialized")

        def _packet_handler(timestamp, packet, *args):
            if not self._stop_event.is_set() and self._callback:
                self._callback(packet, timestamp)

        while not self._stop_event.is_set():
            try:
                # Process a batch of packets
                n = self._pcap.dispatch(self._batch_size, _packet_handler)
                if n == 0:  # No packets available
                    time.sleep(0.001)  # Minimal sleep
            except Exception as e:
                self.logger.error(f"Capture error: {e}")
                break

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
