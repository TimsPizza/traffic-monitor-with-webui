from typing import List, Type
from models.Dtos import (
    FullPacket,
    NetworkStats,
    ProtocolAnalysis,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
)
from .DatabaseOperations import DatabaseOperations


class CrudService:
    def __init__(self):
        self.db_ops = DatabaseOperations()

    @staticmethod
    def _create_dto_from_dict(doc: dict, dto_type: Type) -> object:
        """Factory method to convert MongoDB document to specified DTO type"""
        if dto_type == FullPacket:
            return FullPacket(
                id=str(doc.get("_id", "")),
                src_ip=doc.get("source_ip", ""),
                src_port=doc.get("src_port", -1),
                dst_port=doc.get("dst_port", -1),
                protocol=doc.get("protocol", ""),
                timestamp=doc.get("timestamp", -1),
            )
        elif dto_type == NetworkStats:
            return NetworkStats(**doc)
        elif dto_type == ProtocolAnalysis:
            return ProtocolAnalysis(**doc)
        elif dto_type == TopSourceIP:
            return TopSourceIP(**doc)
        elif dto_type == ProtocolDistribution:
            return ProtocolDistribution(**doc)
        elif dto_type == TrafficSummary:
            return TrafficSummary(**doc)
        elif dto_type == TimeSeriesData:
            return TimeSeriesData(**doc)
        raise ValueError(f"Unsupported DTO type: {dto_type}")

    def find_packets_by_ip(
        self,
        ip_address: str,
        page: int = 1,
        page_size: int = 50,
    ) -> List[FullPacket]:
        """Find all packets from a specific IP address with pagination"""
        raw_data = self.db_ops.find_packets_by_ip(ip_address, page, page_size)
        return [self._create_dto_from_dict(doc, FullPacket) for doc in raw_data]

    def find_packets_by_protocol(
        self,
        protocol: str,
        page: int = 1,
        page_size: int = 50,
    ) -> List[FullPacket]:
        """Find all packets with a specific protocol with pagination"""
        raw_data = self.db_ops.find_packets_by_protocol(protocol, page, page_size)
        return [self._create_dto_from_dict(doc, FullPacket) for doc in raw_data]

    def find_packets_by_timerange(
        self,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[FullPacket]:
        """Find all packets within a specific time range with pagination"""
        raw_data = self.db_ops.find_packets_by_timerange(
            start_time, end_time, page, page_size
        )
        return [self._create_dto_from_dict(doc, FullPacket) for doc in raw_data]

    def get_network_stats(self, start_time: float, end_time: float) -> NetworkStats:
        """Get network statistics for a given time range"""
        return self.db_ops.get_network_stats(start_time, end_time)

    def get_protocol_analysis(
        self, start_time: float, end_time: float
    ) -> ProtocolAnalysis:
        """Get protocol analysis for a given time range"""
        raw_data = self.db_ops.get_protocol_analysis(start_time, end_time)
        return self._create_dto_from_dict(raw_data, ProtocolAnalysis)

    def get_top_source_ips(self, limit: int = 10) -> List[TopSourceIP]:
        """Get top source IPs by packet count"""
        raw_data = self.db_ops.get_top_source_ips(limit)
        return [self._create_dto_from_dict(doc, TopSourceIP) for doc in raw_data]

    def get_protocol_distribution(
        self, start_time: float, end_time: float
    ) -> ProtocolDistribution:
        """Get protocol distribution for a given time range"""
        raw_data = self.db_ops.get_protocol_distribution(start_time, end_time)
        return self._create_dto_from_dict(raw_data, ProtocolDistribution)

    def get_traffic_summary(self, start_time: float, end_time: float) -> TrafficSummary:
        """Get traffic summary for a given time range"""
        raw_data = self.db_ops.get_traffic_summary(start_time, end_time)
        return self._create_dto_from_dict(raw_data, TrafficSummary)

    def get_time_series_data(
        self, start_time: float, end_time: float, interval: int
    ) -> TimeSeriesData:
        """Get time series data for a given time range and interval"""
        return self.db_ops.get_time_series_data(start_time, end_time, interval)

    def delete_packets_before(self, timestamp: float) -> int:
        """Delete all packets before a specific timestamp"""
        return self.db_ops.delete_packets_before(timestamp)

    def close(self):
        """Close the MongoDB connection"""
        self.db_ops.close()
