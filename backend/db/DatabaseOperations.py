import logging
from typing import List, Optional, Type
from pymongo.collection import Collection
from pymongo.database import Database

from packet.Packet import ProcessedPacket
from db.Client import MongoConnectionSingleton
from core.services import ENV_CONFIG
from models.Dtos import NetworkStats, TimeRange, TimeSeriesData, ProtocolDistribution


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
        page: int = 1,
        page_size: int = 50,
    ) -> List[dict]:
        """Find all packets from a specific IP address with pagination"""
        try:
            skip = (page - 1) * page_size
            cursor = (
                self.packets_collection.find({"source_ip": ip_address})
                .skip(skip)
                .limit(page_size)
            )
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error finding packets by IP: {e}")
            return []

    def find_packets_by_protocol(
        self,
        protocol: str,
        page: int = 1,
        page_size: int = 50,
    ) -> List[dict]:
        """Find all packets with a specific protocol with pagination"""
        try:
            skip = (page - 1) * page_size
            cursor = (
                self.packets_collection.find({"protocol": protocol})
                .skip(skip)
                .limit(page_size)
            )
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error finding packets by protocol: {e}")
            return []

    def find_packets_by_timerange(
        self,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[dict]:
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
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error finding packets by time range: {e}")
            return []

    def get_network_stats(self, start_time: float, end_time: float) -> NetworkStats:
        """Get network statistics for a given time range"""
        try:
            # Get basic stats
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                {
                    "$group": {
                        "_id": None,
                        "total_packets": {"$sum": 1},
                        "total_bytes": {"$sum": "$length"},
                        "avg_packet_size": {"$avg": "$length"},
                        "protocols": {"$addToSet": "$protocol"},
                        "source_ips": {"$addToSet": "$source_ip"},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_packets": 1,
                        "total_bytes": 1,
                        "avg_packet_size": 1,
                        "protocol_count": {"$size": "$protocols"},
                        "unique_ips": {"$size": "$source_ips"},
                    }
                },
            ]
            result = self.packets_collection.aggregate(pipeline)
            if not result:
                return NetworkStats()

            # Get protocol distribution
            protocol_dist = self.get_protocol_distribution(start_time, end_time)

            return NetworkStats(
                total_bytes=result.get("total_bytes", 0),
                avg_packet_size=result.get("avg_packet_size", 0),
                protocol_distribution=protocol_dist if protocol_dist else [],
                total_packets=result.get("total_packets", 0),
            )
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return NetworkStats()

    def get_protocol_analysis(self, start_time: float, end_time: float) -> dict:
        """Get protocol analysis for a given time range"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                {
                    "$group": {
                        "_id": "$protocol",
                        "count": {"$sum": 1},
                        "total_bytes": {"$sum": "$length"},
                        "source_ips": {
                            "$push": {
                                "ip": "$source_ip",
                                "count": 1,
                                "total_bytes": "$length",
                            }
                        },
                    }
                },
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            # Convert protocols list to dictionary
            protocol_dict = {
                r["_id"]: {
                    "packet_count": r["count"],
                    "total_bytes": r["total_bytes"],
                    "source_ips": {
                        s["ip"]: {
                            "packet_count": s["count"],
                            "total_bytes": s["total_bytes"],
                            "percentage": (
                                s["count"] / r["count"] if r["count"] > 0 else 0
                            ),
                        }
                        for s in r["source_ips"]
                    },
                    "ports": {},
                    "avg_packet_size": (
                        r["total_bytes"] / r["count"] if r["count"] > 0 else 0
                    ),
                    "time_range": {"start": start_time, "end": end_time},
                }
                for r in results
            }

            total_packets = sum(r["count"] for r in results)
            total_bytes = sum(r["total_bytes"] for r in results)

            from models.Dtos import ProtocolAnalysis

            return ProtocolAnalysis(
                timestamp=start_time,
                packet_count=total_packets,
                total_bytes=total_bytes,
                protocols=protocol_dict,
                intervals=[],
                time_range=TimeRange(start=start_time, end=end_time),
            )
        except Exception as e:
            self.logger.error(f"Error getting protocol analysis: {e}")
            return {"protocols": []}

    def get_top_source_ips(self, limit: int = 10) -> List[dict]:
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
                {
                    "ip": r["_id"],
                    "packet_count": r["count"],
                    "total_bytes": r["total_bytes"],
                    "protocols": {},
                }
                for r in results
            ]
        except Exception as e:
            self.logger.error(f"Error getting top source IPs: {e}")
            return []

    def get_protocol_distribution(
        self, start_time: float, end_time: float
    ) -> List[ProtocolDistribution]:
        """Get protocol distribution for a given time range"""
        try:
            pipeline = [
                # 第一阶段：过滤时间范围
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                # 第二阶段：按时间区间分组，并展开 protocols 信息
                {
                    "$group": {
                        "_id": {
                            "$subtract": [
                                "$timestamp",
                                {"$mod": ["$timestamp", interval]},
                            ]
                        },
                        "protocols": {
                            "$push": {
                                "protocol": "$protocol",
                                "count": 1,
                                "total_bytes": "$length",
                            }
                        },
                    }
                },
                # 第三阶段：展开 protocols 数组
                {"$unwind": "$protocols"},
                # 第四阶段：按时间区间和协议分组，统计每个协议的 count 和 total_bytes
                {
                    "$group": {
                        "_id": {
                            "time_interval": "$_id",
                            "protocol": "$protocols.protocol",
                        },
                        "count": {"$sum": "$protocols.count"},  # 统计协议出现的次数
                        "total_bytes": {
                            "$sum": "$protocols.total_bytes"
                        },  # 统计协议的总字节数
                    }
                },
                # 第五阶段：重新按时间区间分组，整理 protocols 字段
                {
                    "$group": {
                        "_id": "$_id.time_interval",
                        "protocols": {
                            "$push": {
                                "protocol": "$_id.protocol",
                                "count": "$count",
                                "total_bytes": "$total_bytes",
                            }
                        },
                        # 计算总的 count 和 total_bytes
                        "total_count": {"$sum": "$count"},
                        "total_bytes": {"$sum": "$total_bytes"},
                    }
                },
                # 第六阶段：按时间区间排序
                {"$sort": {"_id": 1}},
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            print(results)
            results = results[0]

            total_packets = results.total_count
            total_bytes = results.total_bytes
            protocol_dist_list: List[ProtocolDistribution] = [
                ProtocolDistribution(
                    protocol=item.protocol,
                    percentage=int(
                        round(
                            (item.count / total_packets * 100)
                            if total_packets > 0
                            else 0
                        )
                    ),
                    packet_count=item.count,
                    total_bytes=item.total_bytes,
                )
                for item in results.protocols
            ]
            return results
        except Exception as e:
            self.logger.error(f"Error getting protocol distribution: {e}")
            return {"protocols": []}

    def get_traffic_summary(self, start_time: float, end_time: float) -> dict:
        """Get traffic summary for a given time range"""
        try:
            # Get basic stats
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
            if not result:
                return {
                    "timestamp": start_time,
                    "packet_count": 0,
                    "total_bytes": 0,
                    "top_source_ips": [],
                    "protocol_distribution": [],
                    "intervals": [],
                }

            base_stats = result[0]

            # Get top source IPs
            top_ips = self.get_top_source_ips()
            formatted_top_ips = [
                {
                    "ip": ip["ip"],
                    "packet_count": ip["packet_count"],
                    "total_bytes": ip["total_bytes"],
                    "protocols": ip["protocols"],
                }
                for ip in top_ips
            ]

            # Get protocol distribution
            protocol_dist = self.get_protocol_distribution(start_time, end_time)
            total_packets = base_stats["total_packets"]
            formatted_protocol_dist = [
                {
                    "protocol": p.protocol,
                    "percentage": p.percentage,
                    "packet_count": p.packet_count,
                    "total_bytes": p.total_bytes,
                }
                for p in protocol_dist.protocols
            ]

            from models.Dtos import TrafficSummary

            return TrafficSummary(
                timestamp=start_time,
                packet_count=base_stats.get("total_packets", 0),
                total_bytes=base_stats.get("total_bytes", 0),
                top_source_ips=formatted_top_ips,
                protocol_distribution=formatted_protocol_dist,
                intervals=[],
            )
        except Exception as e:
            self.logger.error(f"Error getting traffic summary: {e}")
            return {}

    def get_time_series_data(
        self, start_time: float, end_time: float, interval: int
    ) -> TimeSeriesData:
        """Get time series data for a given time range and interval"""
        try:
            pipeline = [
                # 第一阶段：过滤时间范围
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                # 第二阶段：按时间区间分组，并展开 protocols 信息
                {
                    "$group": {
                        "_id": {
                            "$subtract": [
                                "$timestamp",
                                {"$mod": ["$timestamp", interval]},
                            ]
                        },
                        "protocols": {
                            "$push": {
                                "protocol": "$protocol",
                                "count": 1,
                                "total_bytes": "$length",
                            }
                        },
                    }
                },
                # 第三阶段：展开 protocols 数组
                {"$unwind": "$protocols"},
                # 第四阶段：按时间区间和协议分组，统计每个协议的 count 和 total_bytes
                {
                    "$group": {
                        "_id": {
                            "time_interval": "$_id",
                            "protocol": "$protocols.protocol",
                        },
                        "count": {"$sum": "$protocols.count"},  # 统计协议出现的次数
                        "total_bytes": {
                            "$sum": "$protocols.total_bytes"
                        },  # 统计协议的总字节数
                    }
                },
                # 第五阶段：重新按时间区间分组，整理 protocols 字段
                {
                    "$group": {
                        "_id": "$_id.time_interval",
                        "protocols": {
                            "$push": {
                                "protocol": "$_id.protocol",
                                "count": "$count",
                                "total_bytes": "$total_bytes",
                            }
                        },
                        # 计算总的 count 和 total_bytes
                        "total_count": {"$sum": "$count"},
                        "total_bytes": {"$sum": "$total_bytes"},
                    }
                },
                # 第六阶段：按时间区间排序
                {"$sort": {"_id": 1}},
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            print(results)
            results = results[0]

            total_packets = results.total_count
            total_bytes = results.total_bytes
            protocol_dist_list: List[ProtocolDistribution] = [
                ProtocolDistribution(
                    protocol=item.protocol,
                    percentage=int(
                        round(
                            (item.count / total_packets * 100)
                            if total_packets > 0
                            else 0
                        )
                    ),
                    packet_count=item.count,
                    total_bytes=item.total_bytes,
                )
                for item in results.protocols
            ]

            return TimeSeriesData(
                packet_count=total_packets,
                total_bytes=total_bytes,
                protocol_distribution=protocol_dist_list,
                time_range=TimeRange(start=float(start_time), end=float(end_time)),
            )
        except Exception as e:
            self.logger.error(f"Error getting time series data: {e}")
            return TimeSeriesData(
                packet_count=0,
                total_bytes=0,
                protocol_distribution=[],
                time_range=TimeRange(start=start_time, end=end_time),
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
