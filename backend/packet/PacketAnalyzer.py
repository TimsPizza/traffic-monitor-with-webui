from threading import Event, Lock
from typing import Dict, List

from models.Dtos import ProtocolPortMappingRuleRecord
from service.GeoIpService import GeoIPSingleton
from core.config import ENV_CONFIG
from .Processors import (
    add_uuid,
    check_application_protocol,
    check_handshake,
    check_src_ip_region,
    check_ssh_type,
    check_tcp,
    check_udp,
)
from .PacketConsumer import PacketConsumer
from .PacketProducer import PacketProducer
from .Packet import CapturedPacket
from packet.utils.DoubleBufferQueue import DoubleBufferQueue
import logging


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

        # 用于同步访问规则映射 (For synchronizing access to rule mappings)
        self._lock = Lock()

        self.logger = logging.getLogger(self.__class__.__name__)

        GeoIPSingleton._load_instance()

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
        self.set_filter("ip and not ether broadcast and not ether multicast")
        self._packet_consumer.add_processor(check_udp)
        self._packet_consumer.add_processor(check_tcp)
        self._packet_consumer.add_processor(check_src_ip_region)
        self._packet_consumer.add_processor(check_application_protocol)
        self._packet_consumer.add_processor(check_ssh_type)
        self._packet_consumer.add_processor(check_handshake)
        self._packet_consumer.add_processor(add_uuid)

        # 端口-协议映射规则 (Port-Protocol mapping rules)
        self._port_protocol_mapping: Dict[int, str] = {}

    def set_interface(self, interface: str):
        """设置抓包接口 (Set capture interface)"""
        self._packet_producer.set_interface(interface)

    def get_active_interface(self) -> str:
        """获取当前活动的抓包接口 (Get current active capture interface)"""
        return self._packet_producer.get_active_interface()

    def get_filter(self) -> str:
        """获取当前过滤器表达式 (Get current filter expression)"""
        return self._packet_producer.filter

    def set_filter(self, filter_expression: str):
        """设置过滤器表达式 (Set filter expression)"""
        try:
            if not filter_expression:
                return
            return self._packet_producer.apply_filter(filter_expression)
        except Exception as e:
            self.logger.error(f"Error setting filter: {e}")

    def set_rules(self, rules: List[ProtocolPortMappingRuleRecord]) -> bool:
        """设置端口-协议映射规则 (Set port-protocol mapping rules)"""
        try:
            with self._lock:
                self._port_protocol_mapping.clear()
                for rule in rules:
                    for port in rule.ports:
                        self._port_protocol_mapping[port] = rule.protocol
            return True
        except Exception as e:
            self.logger.error(f"Error setting rules: {e}")
            return False

    def get_protocol_for_port(self, port: int) -> str:
        """获取指定端口的协议 (Get protocol for specified port)"""
        with self._lock:
            return self._port_protocol_mapping.get(port, "")

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
