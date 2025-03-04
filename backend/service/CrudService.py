from collections import Counter
from logging import Logger
from typing import List, Type, Tuple, Optional, Dict, Any
from core.config import ENV_CONFIG
from models.Dtos import (
    FullPacket,
    NetworkStats,
    PaginatedResponse,
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
        self.logger = Logger(self.__class__.__name__, level=ENV_CONFIG.log_level)

    def _build_paginated_response(
        self,
        raw_data: Dict[str, Any],
        page: int,
        page_size: int,
        data_builder: callable,
    ) -> PaginatedResponse:
        """Build paginated response with error handling"""
        if not raw_data or not raw_data.get("metadata") or not raw_data.get("data"):
            return PaginatedResponse(total=0, page=page, page_size=page_size, data=[])

        meta_data = raw_data["metadata"]
        data = raw_data["data"]
        total_docs = meta_data[0]["total_documents"] if meta_data else 0

        return PaginatedResponse(
            total=total_docs,
            page=page,
            page_size=page_size,
            data=data_builder(data) if data else [],
        )

    def _build_full_packet(self, doc: Dict[str, Any], index: int = 0) -> FullPacket:
        """Build FullPacket from raw document"""
        return FullPacket(
            id=str(doc.get("_id", (index + 1))),
            timestamp=doc.get("timestamp", 0),
            src_ip=doc.get("source_ip", ""),
            dst_port=doc.get("dst_port", 0),
            protocol=doc.get("protocol", ""),
            length=doc.get("length", 0),
            src_region=doc.get("src_region", "Unknown"),
        )

    def find_packets_by_ip(
        self,
        ip_address: str,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[FullPacket]:
        """Find packets by source IP with pagination"""
        raw_data = self.db_ops.find_packets_by_ip(
            ip_address, start_time, end_time, page, page_size
        )

        return self._build_paginated_response(
            raw_data,
            page,
            page_size,
            lambda data: [
                self._build_full_packet(doc, idx) for idx, doc in enumerate(data)
            ],
        )

    def find_packets_by_port(
        self,
        port: int,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[FullPacket]:
        """Find packets by destination port with pagination"""
        raw_data = self.db_ops.find_packets_by_port(
            port, start_time, end_time, page, page_size
        )

        return self._build_paginated_response(
            raw_data,
            page,
            page_size,
            lambda data: [self._build_full_packet(doc) for doc in data],
        )

    def find_packets_by_region(
        self,
        src_region: str,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[FullPacket]:
        """Find packets by src_region with pagination"""
        raw_data = self.db_ops.find_packets_by_region(
            src_region, start_time, end_time, page, page_size
        )

        return self._build_paginated_response(
            raw_data,
            page,
            page_size,
            lambda data: [self._build_full_packet(doc) for doc in data],
        )

    def find_packets_by_protocol(
        self,
        protocol: str,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[FullPacket]:
        """Find all packets with a specific protocol with pagination"""
        raw_data = self.db_ops.find_packets_by_protocol(
            protocol, start_time, end_time, page, page_size
        )

        return self._build_paginated_response(
            raw_data,
            page,
            page_size,
            lambda data: [
                self._build_full_packet(doc, idx) for idx, doc in enumerate(data)
            ],
        )

    def find_packets_by_timerange(
        self,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[FullPacket]:
        """Find all packets within a specific time range with pagination"""
        raw_data = self.db_ops.find_packets_by_timerange(
            start_time, end_time, page, page_size
        )

        return self._build_paginated_response(
            raw_data,
            page,
            page_size,
            lambda data: [
                self._build_full_packet(doc, idx) for idx, doc in enumerate(data)
            ],
        )

    def get_top_source_ips(
        self, start_time: float, end_time: float, page: int, page_size: int
    ) -> PaginatedResponse[TopSourceIP]:
        """Get top source IPs by packet count"""
        try:
            raw_data = self.db_ops.get_top_source_ips(
                start_time, end_time, page, page_size
            )
            meta_data = raw_data["metadata"]
            data = raw_data["data"]
            total_docs = meta_data[0]["total_documents"]
            total_packets = sum(doc["total_packets"] for doc in data)
            total_bytes = sum(doc["total_bytes"] for doc in data)

            top_ips = [
                TopSourceIP(
                    ip=doc["source_ip"],
                    total_packets=doc["total_packets"],
                    total_bytes=doc["total_bytes"],
                    percentage_packets=doc["total_packets"] / total_packets * 100,
                    percentage_bytes=doc["total_bytes"] / total_bytes * 100,
                    src_region=(
                        doc["src_region"] if "src_region" in doc else "Unknown"
                    ),
                )
                for doc in data
            ]
            return PaginatedResponse(
                total=total_docs,
                page=page,
                page_size=page_size,
                data=top_ips,
            )
        except Exception as e:
            self.logger.error(f"Error getting top source IPs: {e}")
            return PaginatedResponse(total=0, page=page, page_size=page_size, data=[])

    def get_protocol_distribution(
        self, start_time: float, end_time: float, page: int = 1, page_size: int = 50
    ) -> PaginatedResponse[ProtocolDistribution]:
        """Get protocol distribution for a given time range"""
        try:
            raw_data = self.db_ops.get_protocol_distribution(
                start_time, end_time, page, page_size
            )
            meta_data = raw_data["metadata"]
            data = raw_data["data"]

            total_packets = sum(doc["total_packets"] for doc in data)
            total_bytes = sum(doc["total_bytes"] for doc in data)
            total_docs = meta_data[0]["total_documents"]
            distribution_items = [
                ProtocolDistributionItem(
                    protocol=doc["protocol"],
                    percentage_count=doc["total_packets"] / total_packets * 100,
                    percentage_bytes=doc["total_bytes"] / total_bytes * 100,
                    packet_count=doc["total_packets"],
                    total_bytes=doc["total_bytes"],
                )
                for doc in data
            ]
            distribution = ProtocolDistribution(
                distribution=distribution_items,
                time_range=TimeRange(start=start_time, end=end_time),
            )
            return PaginatedResponse(
                total=total_docs,
                page=page,
                page_size=page_size,
                data=distribution,
            )
        except Exception as e:
            self.logger.error(f"Error getting protocol distribution: {e}")
            return PaginatedResponse(total=0, page=page, page_size=page_size, data=[])

    def get_traffic_summary(
        self, start_time: float, end_time: float, page: int = 1, page_size: int = 50
    ) -> PaginatedResponse[TrafficSummary]:
        """Get traffic summary for a given time range"""
        top_ips = self.get_top_source_ips(start_time, end_time, page, page_size)
        protocol_dist = self.get_protocol_distribution(
            start_time, end_time, page, page_size
        )

        summary = TrafficSummary(
            total_packets=sum(ip.total_packets for ip in top_ips.data),
            total_bytes=sum(ip.total_bytes for ip in top_ips.data),
            top_source_ips=top_ips.data,
            protocol_distribution=protocol_dist.data,
            time_range=TimeRange(start=start_time, end=end_time),
        )

        return PaginatedResponse(
            total=1,  # only 1 for the summary
            page=page,
            page_size=page_size,
            data=summary,
        )

    def get_time_series_data(
        self,
        start_time: float,
        end_time: float,
        interval: int,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[TimeSeriesData]:
        """Get time series data for a given time range and interval"""
        try:

            raw_data = self.db_ops.get_time_series_data(
                start_time, end_time, interval, page, page_size
            )
            meta_data = raw_data["metadata"]
            data = raw_data["data"]
            total_docs = meta_data[0]["total_documents"]
            time_series = [
                TimeSeriesData(
                    time_range=TimeRange(start=doc["start_time"], end=doc["end_time"]),
                    total_packets=doc["total_packets"],
                    total_bytes=doc["total_bytes"],
                )
                for doc in data
            ]
            return PaginatedResponse(
                total=total_docs,
                page=page,
                page_size=page_size,
                data=time_series,
            )
        except Exception as e:
            self.logger.error(f"Error getting time series data: {e}")
            return PaginatedResponse(total=0, page=page, page_size=page_size, data=[])

    def delete_packets_before(self, timestamp: float) -> int:
        """Delete all packets before a specific timestamp"""
        return self.db_ops.delete_packets_before(timestamp)

    def close(self):
        """Close the MongoDB connection"""
        self.db_ops.close()
