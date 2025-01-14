import logging
from typing import Any, Dict, List, Optional, Type
from pymongo.collection import Collection
from pymongo.database import Database

from db.QueryExecutor import QueryExecutor
from packet.Packet import ProcessedPacket
from db.Client import MongoConnectionSingleton
from core.services import ENV_CONFIG
from models.Dtos import (
    FullPacket,
    NetworkStats,
    ProtocolAnalysis,
    TimeRange,
    TimeSeriesData,
    ProtocolDistribution,
    TopSourceIP,
    TrafficSummary,
)


class DatabaseOperations:
    def __init__(self):
        self.client = MongoConnectionSingleton.get_instance()
        self.db: Database = self.client.get_database(ENV_CONFIG.database_name)
        self.packets_collection: Collection = self.db.get_collection(
            ENV_CONFIG.captured_packet_collection_name
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self._create_indexes()

    def _create_indexes(self):
        """Create necessary indexes for better query performance"""
        self.packets_collection.create_index([("timestamp", -1)])
        self.packets_collection.create_index([("source_ip", 1)])
        self.packets_collection.create_index([("protocol", 1)])

    def insert_packet(self, packet: ProcessedPacket) -> bool:
        """Insert a single processed packet into the database"""
        try:
            packet_dict = {
                "timestamp": packet.timestamp,
                "layer": packet.layer,
                "source_ip": packet.source_ip,
                "src_port": packet.src_port,
                "dst_port": packet.dst_port,
                "protocol": packet.protocol,
                "length": packet.length,
            }
            result = self.packets_collection.insert_one(packet_dict)
            return bool(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error inserting packet: {e}")
            return False

    def insert_many_packets(self, packets: List[ProcessedPacket]) -> int:
        """Insert multiple processed packets into the database"""
        try:
            packet_dicts = [
                {
                    "id": packet.id,
                    "timestamp": packet.timestamp,
                    "layer": packet.layer,
                    "source_ip": packet.source_ip,
                    "src_port": packet.src_port,
                    "dst_port": packet.dst_port,
                    "protocol": packet.protocol,
                }
                for packet in packets
            ]
            result = self.packets_collection.insert_many(packet_dicts)
            return len(result.inserted_ids)
        except Exception as e:
            self.logger.error(f"Error inserting multiple packets: {e}")
            return 0

    def find_packets_by_ip(
        self,
        ip_address: str,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find all packets from a specific IP address with pagination"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.find_packets_by_ip(
            ip_address, start_time, end_time, page, page_size
        )

    def find_packets_by_protocol(
        self,
        protocol: str,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find all packets with a specific protocol with pagination"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.find_packets_by_protocol(protocol, page, page_size)

    def find_packets_by_timerange(
        self,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find all packets within a specific time range with pagination"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.find_packets_by_time_range(
            start_time, end_time, page, page_size
        )

    def get_network_stats(
        self, start_time: float, end_time: float
    ) -> List[Dict[str, Any]]:
        """Get network statistics for a given time range"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.get_network_stats(start_time, end_time)

    def get_protocol_analysis(
        self, start_time: float, end_time: float
    ) -> List[Dict[str, Any]]:
        """Get protocol analysis for a given time range"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.get_protocol_distribution(start_time, end_time)

    def get_top_source_ips(
        self, start_time: float, end_time: float, page: int, page_size: int
    ) -> List[Dict[str, Any]]:
        """Get top source IPs by packet count"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.get_top_source_ips(start_time, end_time, page, page_size)

    def get_protocol_distribution(
        self, start_time: float, end_time: float
    ) -> List[ProtocolDistribution]:
        """Get protocol distribution for a given time range"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.get_protocol_distribution(start_time, end_time)

    def get_traffic_summary(
        self, start_time: float, end_time: float
    ) -> List[Dict[str, Any]]:
        """Get traffic summary for a given time range"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.get_traffic_summary(start_time, end_time)

    def get_time_series_data(
        self, start_time: float, end_time: float, interval: int
    ) -> List[Dict[str, Any]]:
        """Get time series data for a given time range and interval"""
        query_executor = QueryExecutor(self.packets_collection)
        return query_executor.get_time_series_data(start_time, end_time, interval)

    def delete_packets_before(self, timestamp: float) -> int:
        """Delete all packets before a specific timestamp"""
        try:
            result = self.packets_collection.delete_many(
                {"timestamp": {"$lt": timestamp}}
            )
            return result.deleted_count
        except Exception as e:
            self.logger.error(f"Error deleting old packets: {e}")
            return 0

    def close(self):
        """Close the MongoDB connection"""
        self.client.close()
