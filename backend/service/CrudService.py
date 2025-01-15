from collections import Counter
from typing import List, Type
from models.Dtos import (
    FullPacket,
    NetworkStats,
    ProtocolAnalysis,
    ProtocolDistributionItem,
    TimeRange,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
)
from db.DatabaseOperations import DatabaseOperations


class CrudService:
    def __init__(self):
        self.db_ops = DatabaseOperations()

    def find_packets_by_ip(
        self,
        ip_address: str,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[FullPacket]:
        """Find all packets from a specific IP address with pagination"""
        raw_data = self.db_ops.find_packets_by_ip(
            ip_address, start_time, end_time, page, page_size
        )
        return [
            FullPacket(
                id=str(doc["_id"]),
                timestamp=doc["timestamp"],
                src_ip=doc["source_ip"],
                dst_port=doc["dst_port"],
                protocol=doc["protocol"],
                length=doc["length"],
                region=(
                    doc["region"]
                    if "region" in doc and doc["region"] is not None
                    else "Unknown"
                ),
            )
            for doc in raw_data
        ]

    def find_packets_by_protocol(
        self,
        protocol: str,
        page: int = 1,
        page_size: int = 50,
    ) -> List[FullPacket]:
        """Find all packets with a specific protocol with pagination"""
        raw_data = self.db_ops.find_packets_by_protocol(protocol, page, page_size)
        return [
            FullPacket(
                id=str(doc["_id"]),
                timestamp=doc["timestamp"],
                src_ip=doc["source_ip"],
                dst_port=doc["dst_port"],
                protocol=doc["protocol"],
                length=doc["length"],
                region=(
                    doc["region"]
                    if "region" in doc and doc["region"] is not None
                    else "Unknown"
                ),
            )
            for doc in raw_data
        ]

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
        return [
            FullPacket(
                id=str(doc["_id"]),
                timestamp=doc["timestamp"],
                src_ip=doc["source_ip"],
                dst_port=doc["dst_port"],
                protocol=doc["protocol"],
                region=(
                    doc["region"]
                    if "region" in doc and doc["region"] is not None
                    else "Unknown"
                ),
            )
            for doc in raw_data
        ]

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
        self, start_time: float, end_time: float, page: int = 1, page_size: int = 99999
    ) -> List[TopSourceIP]:
        """Get top source IPs by packet count"""
        raw_data = self.db_ops.get_top_source_ips(start_time, end_time, page, page_size)
        return [
            TopSourceIP(
                ip=doc["source_ip"],
                total_packets=doc["total_packets"],
                total_bytes=doc["total_bytes"],
                region=(
                    doc["region"]
                    if "region " in doc and doc["region"] is not None
                    else "Unknown"
                ),
            )
            for doc in raw_data
        ]

    def get_protocol_distribution(
        self, start_time: float, end_time: float, page: int = 1, page_size: int = 99999
    ) -> ProtocolDistribution:
        """Get protocol distribution for a given time range"""
        raw_data = self.db_ops.get_protocol_distribution(start_time, end_time)
        total_packets = sum(doc["total_packets"] for doc in raw_data)
        total_bytes = sum(doc["total_bytes"] for doc in raw_data)
        distribution = [
            ProtocolDistributionItem(
                protocol=doc["protocol"],
                percentage_count=doc["total_packets"] / total_packets * 100,
                percentage_bytes=doc["total_bytes"] / total_bytes * 100,
                packet_count=doc["total_packets"],
                total_bytes=doc["total_bytes"],
            )
            for doc in raw_data
        ]
        return ProtocolDistribution(
            distribution=distribution,
            time_range=TimeRange(start=start_time, end=end_time),
        )

    def get_traffic_summary(
        self, start_time: float, end_time: float, page: int = 1, page_size: int = 99999
    ) -> TrafficSummary:
        """Get traffic summary for a given time range"""
        top_ips = self.get_top_source_ips(start_time, end_time, page, page_size)
        protocol_dist = self.get_protocol_distribution(
            start_time, end_time, page, page_size
        )
        return TrafficSummary(
            total_packets=sum(ip.total_packets for ip in top_ips),
            total_bytes=sum(ip.total_bytes for ip in top_ips),
            top_source_ips=top_ips,
            protocol_distribution=protocol_dist,
            time_range=TimeRange(start=start_time, end=end_time),
        )

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
