import logging
from typing import List, Optional, Type
from pymongo.collection import Collection
from pymongo.database import Database

from packet.Packet import ProcessedPacket
from db.Client import MongoConnectionSingleton
from core.services import ENV_CONFIG
from models.Dtos import (
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
            results = list(self.packets_collection.aggregate(pipeline))[0]
            print(results)
            if not results:
                return NetworkStats()

            # Get protocol distribution
            protocol_dist = self.get_protocol_distribution(start_time, end_time)
            print(protocol_dist)

            return NetworkStats(
                total_bytes=results["total_bytes"],
                avg_packet_size=results["avg_packet_size"],
                protocol_distribution=protocol_dist,
                total_packets=results["total_packets"],
            )
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return NetworkStats()

    def get_protocol_analysis(
        self, start_time: float, end_time: float
    ) -> List[ProtocolAnalysis]:
        """Get protocol analysis for a given time range"""
        try:
            pipeline = [
                # 第一阶段：过滤时间段内的数据
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                # 第二阶段：按 protocol 分组，统计总数据包数、总字节数、源 IP 列表、端口列表
                {
                    "$group": {
                        "_id": "$protocol",  # 按协议分组
                        "packet_count": {"$sum": 1},  # 统计该协议的总数据包数
                        "total_bytes": {"$sum": "$length"},  # 统计该协议的总字节数
                        "source_ips": {
                            "$addToSet": "$source_ip"
                        },  # 收集所有源 IP（去重）
                        "ports": {"$addToSet": "$port"},  # 收集所有端口（去重）
                    }
                },
                # 第三阶段：计算平均数据包大小，并整理输出格式
                {
                    "$project": {
                        "_id": 0,  # 移除 _id 字段
                        "protocol": "$_id",  # 协议名称
                        "packet_count": 1,  # 总数据包数
                        "source_ips": 1,  # 源 IP 列表
                        "ports": 1,  # 端口列表
                        "avg_packet_size": {
                            "$divide": [
                                "$total_bytes",
                                "$packet_count",
                            ]  # 计算平均数据包大小
                        },
                    }
                },
            ]
            results = list(self.packets_collection.aggregate(pipeline))

            # Convert protocols list to dictionary
            return [
                ProtocolAnalysis(
                    protocol=r["protocol"],
                    avg_packet_size=r["avg_packet_size"],
                    ports=r["ports"],
                    source_ips=r["source_ips"],
                    packet_count=r["packet_count"],
                )
                for r in results
            ]
        except Exception as e:
            self.logger.error(f"Error getting protocol analysis: {e}")
            return {"protocols": []}

    def get_top_source_ips(self, limit: int = 10) -> List[TopSourceIP]:
        """Get top source IPs by packet count with protocol distribution"""
        try:
            pipeline = [
                # 第一阶段：按 source_ip 分组，统计总数据包数和总字节数，并收集所有协议
                {
                    "$group": {
                        "_id": "$source_ip",
                        "count": {"$sum": 1},  # 统计每个 source_ip 的数据包数
                        "total_bytes": {
                            "$sum": "$length"
                        },  # 统计每个 source_ip 的总字节数
                        "protocols": {"$push": "$protocol"},  # 收集所有协议
                    }
                },
                # 第二阶段：展开 protocols 数组，按 source_ip 和 protocol 分组统计
                {"$unwind": "$protocols"},
                {
                    "$group": {
                        "_id": {
                            "source_ip": "$_id",  # 保留 source_ip
                            "protocol": "$protocols",  # 按协议分组
                        },
                        "count": {"$sum": 1},  # 统计每个协议的出现次数
                        "total_bytes": {"$first": "$total_bytes"},  # 保留总字节数
                    }
                },
                # 第三阶段：重新按 source_ip 分组，整理 protocols 字段
                {
                    "$group": {
                        "_id": "$_id.source_ip",
                        "count": {"$first": "$count"},  # 保留总数据包数
                        "total_bytes": {"$first": "$total_bytes"},  # 保留总字节数
                        "protocols": {
                            "$push": {
                                "protocol": "$_id.protocol",
                                "count": "$count",  # 每个协议的出现次数
                            }
                        },
                    }
                },
                # 第四阶段：按 count 降序排列
                {"$sort": {"count": -1}},
                # 第五阶段：限制结果数量
                {"$limit": limit},
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            return [
                TopSourceIP(
                    ip=r["_id"],
                    packet_count=r["count"],
                    total_bytes=r["total_bytes"],
                    protocols=r["protocols"],
                )
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
                # 第一阶段：过滤时间段内的数据
                {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}},
                # 第二阶段：按协议分组，统计每个协议的数据包数和字节数
                {
                    "$group": {
                        "_id": "$protocol",  # 按协议分组
                        "count": {"$sum": 1},  # 统计每个协议的数据包数
                        "total_bytes": {"$sum": "$length"},  # 统计每个协议的总字节数
                    }
                },
                # 第三阶段：计算总数据包数和总字节数
                {
                    "$group": {
                        "_id": None,  # 合并所有分组
                        "protocols": {
                            "$push": {
                                "protocol": "$_id",  # 协议名称
                                "count": "$count",  # 每个协议的数据包数
                                "total_bytes": "$total_bytes",  # 每个协议的总字节数
                            }
                        },
                        "total_count": {"$sum": "$count"},  # 总数据包数
                        "total_bytes": {"$sum": "$total_bytes"},  # 总字节数
                    }
                },
                # 第四阶段：计算每个协议的占比
                {
                    "$project": {
                        "_id": 0,  # 移除 _id 字段
                        "protocols": {
                            "$map": {
                                "input": "$protocols",
                                "as": "p",
                                "in": {
                                    "protocol": "$$p.protocol",
                                    "count": "$$p.count",
                                    "total_bytes": "$$p.total_bytes",
                                    "percentage": {
                                        "$multiply": [
                                            {
                                                "$divide": ["$$p.count", "$total_count"]
                                            },  # 计算占比
                                            100,  # 转换为百分比
                                        ]
                                    },
                                },
                            }
                        },
                        "total_count": 1,  # 保留总数据包数
                        "total_bytes": 1,  # 保留总字节数
                    }
                },
                # 第五阶段：对 protocols 数组按 percentage 降序排列
                {
                    "$project": {
                        "protocols": {
                            "$sortArray": {
                                "input": "$protocols",
                                "sortBy": {"percentage": -1},  # 按 percentage 降序排列
                            }
                        },
                        "total_count": 1,
                        "total_bytes": 1,
                    }
                },
            ]
            results = list(self.packets_collection.aggregate(pipeline))
            results = results[0]

            total_packets = results["total_count"]
            total_bytes = results["total_bytes"]
            protocol_dist_list: List[ProtocolDistribution] = [
                ProtocolDistribution(
                    protocol=item["protocol"],
                    percentage=(
                        round(
                            (item["count"] / total_packets * 100)
                            if total_packets > 0
                            else 0
                        )
                    ),
                    packet_count=item["count"],
                    total_bytes=item["total_bytes"],
                )
                for item in results["protocols"]
            ]
            return protocol_dist_list
        except Exception as e:
            self.logger.error(f"Error getting protocol distribution: {e}")
            return {"protocols": []}

    def get_traffic_summary(self, start_time: float, end_time: float) -> TrafficSummary:
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
                return TrafficSummary()

            base_stats = result[0]

            # Get top source IPs
            top_ips = self.get_top_source_ips()

            # Get protocol distribution
            protocol_dist = self.get_protocol_distribution(start_time, end_time)

            return TrafficSummary(
                total_bytes=base_stats.get("total_bytes", 0),
                top_source_ips=top_ips,
                protocol_distribution=protocol_dist,
                time_range=TimeRange(
                    start=start_time,
                    end=end_time,
                ),
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
            results = results[0]

            total_packets = results["total_count"]
            total_bytes = results["total_bytes"]
            protocol_dist_list: List[ProtocolDistribution] = [
                ProtocolDistribution(
                    protocol=item["protocol"],
                    percentage=(
                        round(
                            (item["count"] / total_packets * 100)
                            if total_packets > 0
                            else 0
                        )
                    ),
                    packet_count=item["count"],
                    total_bytes=item["total_bytes"],
                )
                for item in results["protocols"]
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
