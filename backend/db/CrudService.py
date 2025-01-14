from collections import Counter
from typing import List, Type
from models.Dtos import (
    FullPacket,
    NetworkStats,
    ProtocolAnalysis,
    TimeRange,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
)
from .DatabaseOperations import DatabaseOperations


class CrudService:
    def __init__(self):
        self.db_ops = DatabaseOperations()

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

    def get_network_stats(self, start_time: float, end_time: float) -> NetworkStats:
        """Get network statistics for a given time range"""
        raw_data = self.db_ops.get_network_stats(start_time, end_time)
        total_packets = sum(doc["total_packets"] for doc in raw_data)
        total_bytes = sum(doc["total_bytes"] for doc in raw_data)
        avg_packet_size = total_bytes / total_packets if total_packets > 0 else 0
        protocol_distribution = [
            ProtocolDistribution(
                protocol=doc["protocol"],
                percentage_count=doc["total_packets"] / total_packets * 100,
                percentage_bytes=doc["total_bytes"] / total_bytes * 100,
                packet_count=doc["total_packets"],
                total_bytes=doc["total_bytes"],
            )
            for doc in raw_data
        ]
        return NetworkStats(
            total_packets=total_packets,
            total_bytes=total_bytes,
            avg_packet_size=avg_packet_size,
            protocol_distribution=protocol_distribution,
        )

    def get_protocol_analysis(
        self, start_time: float, end_time: float
    ) -> List[ProtocolAnalysis]:
        """Get protocol analysis for a given time range"""
        raw_data = self.db_ops.get_protocol_analysis(start_time, end_time)
        return [
            ProtocolAnalysis(
                protocol=doc["protocol"],
                packet_count=doc["total_packets"],
                source_ips=doc["source_ips"],
                avg_packet_size=(
                    doc["total_bytes"] / doc["total_packets"]
                    if doc["total_packets"] > 0
                    else 0
                ),
            )
            for doc in raw_data
        ]

    def get_top_source_ips(
        self, start_time: float, end_time: float, page: int, page_size: int
    ) -> List[TopSourceIP]:
        """Get top source IPs by packet count"""
        raw_data = self.db_ops.get_top_source_ips(start_time, end_time, page, page_size)
        ips = [doc["source_ip"] for doc in raw_data]
        ip_records = [
            {
                "ip": ip,
                "records": self.db_ops.find_packets_by_ip(
                    ip, start_time, end_time, page, page_size=999999
                ),
            }
            for ip in ips
        ]

        ip_protocol_counts_map = [
            {
                "ip": r["ip"],
                "protocols": [(dict(Counter(doc["protocol"] for doc in r["records"])))],
            }
            for r in ip_records
        ]
        return [
            TopSourceIP(
                ip=doc["source_ip"],
                packet_count=doc["total_packets"],
                total_bytes=doc["total_bytes"],
                protocols=ip_protocol_counts_map[ips.index(doc["source_ip"])][
                    "protocols"
                ],
            )
            for doc in raw_data
        ].sort(key=lambda x: x.packet_count, reverse=True)

    def get_protocol_distribution(
        self, start_time: float, end_time: float
    ) -> List[ProtocolDistribution]:
        """Get protocol distribution for a given time range"""
        raw_data = self.db_ops.get_protocol_distribution(start_time, end_time)
        total_packets = sum(doc["total_packets"] for doc in raw_data)
        total_bytes = sum(doc["total_bytes"] for doc in raw_data)
        return [
            ProtocolDistribution(
                protocol=doc["protocol"],
                percentage_count=doc["total_packets"] / total_packets * 100,
                percentage_bytes=doc["total_bytes"] / total_bytes * 100,
                packet_count=doc["total_packets"],
                total_bytes=doc["total_bytes"],
            )
            for doc in raw_data
        ]

    def get_traffic_summary(self, start_time: float, end_time: float) -> TrafficSummary:
        """Get traffic summary for a given time range"""
        return self.db_ops.get_traffic_summary(start_time, end_time)

    def get_time_series_data(
        self, start_time: float, end_time: float, interval: int
    ) -> TimeSeriesData:
        """Get time series data for a given time range and interval"""
        raw_data = self.db_ops.get_time_series_data(start_time, end_time, interval)
        return [
            TimeSeriesData(
                time_range=TimeRange(
                    start=doc["timestamp"], end=doc["timestamp"] + interval
                ),
                total_packets=doc["total_packets"],
                total_bytes=doc["total_bytes"],
            )
            for doc in raw_data
        ]

    def delete_packets_before(self, timestamp: float) -> int:
        """Delete all packets before a specific timestamp"""
        return self.db_ops.delete_packets_before(timestamp)

    def close(self):
        """Close the MongoDB connection"""
        self.db_ops.close()
