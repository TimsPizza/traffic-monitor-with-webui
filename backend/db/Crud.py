import logging
from typing import List, Optional, Type
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from models.Dtos import (
    FullPacket,
    BasicPacket,
    NetworkStats,
    ProtocolAnalysis,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
)
from models.Filter import Protocol
from db.Client import MongoConnectionSingleton
from core.services import ENV_CONFIG
from packet.Packet import ProcessedPacket


class PacketDB:
    def __init__(self):
        self.client = MongoConnectionSingleton.get_instance()
        self.db: Database = self.client.get_database(ENV_CONFIG.database_name)

        self.packets_collection: Collection = self.db.get_collection(
            ENV_CONFIG.captured_packet_collection_name
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create indexes for better query performance
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
        page: int = 1,
        page_size: int = 50,
        dto_type: Type = FullPacket,
    ) -> List:
        """Find all packets from a specific IP address with pagination"""
        try:
            skip = (page - 1) * page_size
            cursor = (
                self.packets_collection.find({"source_ip": ip_address})
                .skip(skip)
                .limit(page_size)
            )
            return [self._create_dto_from_dict(doc, dto_type) for doc in cursor]
        except Exception as e:
            self.logger.error(f"Error finding packets by IP: {e}")
            return []

    def find_packets_by_protocol(
        self,
        protocol: str,
        page: int = 1,
        page_size: int = 50,
        dto_type: Type = FullPacket,
    ) -> List:
        """Find all packets with a specific protocol with pagination"""
        try:
            skip = (page - 1) * page_size
            cursor = (
                self.packets_collection.find({"protocol": protocol})
                .skip(skip)
                .limit(page_size)
            )
            return [self._create_dto_from_dict(doc, dto_type) for doc in cursor]
        except Exception as e:
            self.logger.error(f"Error finding packets by protocol: {e}")
            return []

    def find_packets_by_timerange(
        self,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
        dto_type: Type = FullPacket,
    ) -> List:
        """Find all packets within a specific time range with pagination"""
        try:
            skip = (page - 1) * page_size
            cursor = (
                self.packets_collection.find(
                    {"timestamp": {"$gte": start_time, "$lte": end_time}}
                )
                .skip(skip)
                .limit(page_size)
            )
            return [self._create_dto_from_dict(doc, dto_type) for doc in cursor]
        except Exception as e:
            self.logger.error(f"Error finding packets by time range: {e}")
            return []

    def get_network_stats(self, start_time: float, end_time: float) -> NetworkStats:
        """Get network statistics for a given time range"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                {
                    "$group": {
                        "_id": None,
                        "total_packets": {"$sum": 1},
                        "total_bytes": {"$sum": "$length"},
                        "avg_packet_size": {"$avg": "$length"},
                        "max_packet_size": {"$max": "$length"},
                        "min_packet_size": {"$min": "$length"},
                    }
                },
            ]
            result = list(self.packets_collection.aggregate(pipeline))
            if result:
                return NetworkStats(**result[0])
            return NetworkStats()
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return NetworkStats()

    def get_protocol_analysis(
        self, start_time: float, end_time: float
    ) -> ProtocolAnalysis:
        """Get protocol analysis for a given time range"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                {
                    "$group": {
                        "_id": "$protocol",
                        "count": {"$sum": 1},
                        "total_bytes": {"$sum": "$length"},
                    }
                },
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            return ProtocolAnalysis(
                protocols=[
                    {
                        "protocol": r["_id"],
                        "count": r["count"],
                        "total_bytes": r["total_bytes"],
                    }
                    for r in results
                ]
            )
        except Exception as e:
            self.logger.error(f"Error getting protocol analysis: {e}")
            return ProtocolAnalysis()

    def get_top_source_ips(self, limit: int = 10) -> List[TopSourceIP]:
        """Get top source IPs by packet count"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$source_ip",
                        "count": {"$sum": 1},
                        "total_bytes": {"$sum": "$length"},
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": limit},
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            return [
                TopSourceIP(ip=r["_id"], count=r["count"], total_bytes=r["total_bytes"])
                for r in results
            ]
        except Exception as e:
            self.logger.error(f"Error getting top source IPs: {e}")
            return []

    def get_protocol_distribution(
        self, start_time: float, end_time: float
    ) -> ProtocolDistribution:
        """Get protocol distribution for a given time range"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                {"$group": {"_id": "$protocol", "count": {"$sum": 1}}},
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            return ProtocolDistribution(
                protocols=[{"protocol": r["_id"], "count": r["count"]} for r in results]
            )
        except Exception as e:
            self.logger.error(f"Error getting protocol distribution: {e}")
            return ProtocolDistribution()

    def get_traffic_summary(self, start_time: float, end_time: float) -> TrafficSummary:
        """Get traffic summary for a given time range"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                {
                    "$group": {
                        "_id": None,
                        "total_packets": {"$sum": 1},
                        "total_bytes": {"$sum": "$length"},
                        "start_time": {"$min": "$timestamp"},
                        "end_time": {"$max": "$timestamp"},
                    }
                },
            ]
            result = list(self.packets_collection.aggregate(pipeline))
            if result:
                return TrafficSummary(**result[0])
            return TrafficSummary()
        except Exception as e:
            self.logger.error(f"Error getting traffic summary: {e}")
            return TrafficSummary()

    def get_time_series_data(
        self, start_time: float, end_time: float, interval: int
    ) -> TimeSeriesData:
        """Get time series data for a given time range and interval"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                {
                    "$group": {
                        "_id": {
                            "$subtract": [
                                "$timestamp",
                                {"$mod": ["$timestamp", interval]},
                            ]
                        },
                        "count": {"$sum": 1},
                        "total_bytes": {"$sum": "$length"},
                    }
                },
                {"$sort": {"_id": 1}},
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            return TimeSeriesData(
                intervals=[
                    {
                        "timestamp": r["_id"],
                        "count": r["count"],
                        "total_bytes": r["total_bytes"],
                    }
                    for r in results
                ]
            )
        except Exception as e:
            self.logger.error(f"Error getting time series data: {e}")
            return TimeSeriesData()

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
        elif dto_type == BasicPacket:
            return BasicPacket(
                src_ip=doc.get("source_ip", ""),
                dst_ip=doc.get("destination_ip", ""),
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

    @staticmethod
    def _create_packet_from_dict(doc: dict) -> ProcessedPacket:
        """Convert a MongoDB document to a ProcessedPacket object"""
        return ProcessedPacket(
            timestamp=doc.get("timestamp", -1),
            layer=doc.get("layer", ""),
            source_ip=doc.get("source_ip", ""),
            src_port=doc.get("src_port", -1),
            dst_port=doc.get("dst_port", -1),
            protocol=doc.get("protocol", ""),
        )

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


MONGO_DB = PacketDB()


# Export query methods
async def get_packets_by_time_range(
    start_time: float,
    end_time: float,
    page: int = 1,
    page_size: int = 50,
    dto_type: Type = FullPacket,
) -> List:
    return MONGO_DB.find_packets_by_timerange(
        start_time, end_time, page, page_size, dto_type
    )


async def get_packets_by_protocol(
    protocol: str, page: int = 1, page_size: int = 50, dto_type: Type = FullPacket
) -> List:
    return MONGO_DB.find_packets_by_protocol(protocol, page, page_size, dto_type)


async def get_packets_by_source_ip(
    ip_address: str, page: int = 1, page_size: int = 50, dto_type: Type = FullPacket
) -> List:
    return MONGO_DB.find_packets_by_ip(ip_address, page, page_size, dto_type)


async def get_network_stats(start_time: float, end_time: float) -> NetworkStats:
    return MONGO_DB.get_network_stats(start_time, end_time)


async def get_protocol_analysis(start_time: float, end_time: float) -> ProtocolAnalysis:
    return MONGO_DB.get_protocol_analysis(start_time, end_time)


async def get_top_source_ips(limit: int = 10) -> List[TopSourceIP]:
    return MONGO_DB.get_top_source_ips(limit)


async def get_protocol_distribution(
    start_time: float, end_time: float
) -> ProtocolDistribution:
    return MONGO_DB.get_protocol_distribution(start_time, end_time)


async def get_traffic_summary(start_time: float, end_time: float) -> TrafficSummary:
    return MONGO_DB.get_traffic_summary(start_time, end_time)


async def get_time_series_data(
    start_time: float, end_time: float, interval: int
) -> TimeSeriesData:
    return MONGO_DB.get_time_series_data(start_time, end_time, interval)
