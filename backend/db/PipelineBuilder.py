from abc import ABC, abstractmethod
from attr import dataclass
from pymongo.collection import Collection
from typing import Any, Dict, List, Union


class GroupBy:
    @staticmethod
    def source_ip() -> Dict[str, Any]:
        return {
            "_id": None,
            "source_ip": {"$first": "$source_ip"},
            "count": {"$sum": 1},
            "total_bytes": {"$sum": "$length"},
            "region": {"$first": "$src_region"},
        }

    @staticmethod
    def top_source_ips() -> Dict[str, Any]:
        return {
            "_id": "$source_ip",
            "total_packets": {"$sum": 1},
            "total_bytes": {"$sum": "$length"},
            "src_region": {"$first": "$src_region"},
        }

    @staticmethod
    def protocol() -> Dict[str, Any]:
        return {
            "_id": "$protocol",
            "total_bytes": {"$sum": "$length"},
            "total_packets": {"$sum": 1},
            # "source_ips": {"$addToSet": "$source_ip"},
        }

    @staticmethod
    def time_interval(interval: int) -> Dict[str, Any]:
        return {
            "_id": {"$subtract": ["$timestamp", {"$mod": ["$timestamp", interval]}]},
            "total_packets": {"$sum": 1},
            "total_bytes": {"$sum": "$length"},
        }

    @staticmethod
    def traffic_summary() -> Dict[str, Any]:
        return {
            "_id": None,
            "total_packets": {"$sum": 1},
            "total_bytes": {"$sum": "$length"},
            # "unique_ips": {"$addToSet": "$source_ip"},
            "protocols": {"$addToSet": "$protocol"},
        }


class ProjectBy:
    @staticmethod
    def time_interval(interval: int) -> Dict[str, Any]:
        return {
            "_id": 0,
            "start_time": "$_id",
            "end_time": {"$add": ["$_id", interval]},
            "total_packets": 1,
            "total_bytes": 1,
        }

    @staticmethod
    def top_source_ips() -> Dict[str, Any]:
        return {
            "_id": 0,
            "source_ip": "$_id",
            "total_bytes": 1,
            "total_packets": 1,
            "src_region": 1,
        }

    @staticmethod
    def traffic_summary() -> Dict[str, Any]:
        return {
            "_id": 0,
            "total_packets": 1,
            "total_bytes": 1,
            "protocols": 1,
        }

    @staticmethod
    def protocol() -> Dict[str, Any]:
        return {
            "_id": 0,
            "protocol": "$_id",
            "total_packets": 1,
            "total_bytes": 1,
            # "source_ips": 1,
        }


class MatchBy:
    @staticmethod
    def time_range(start_time: float, end_time: float) -> Dict[str, Any]:
        return {"timestamp": {"$gte": start_time, "$lte": end_time}}

    @staticmethod
    def source_ip(source_ip: str) -> Dict[str, Any]:
        return {"source_ip": source_ip}

    @staticmethod
    def protocol(protocol: str) -> Dict[str, Any]:
        return {"protocol": protocol}

    @staticmethod
    def region(region: str) -> Dict[str, Any]:
        return {"src_region": region}

    @staticmethod
    def port(port: int) -> Dict[str, Any]:
        return {"dst_port": port}


class SortBy:
    @staticmethod
    def total_packets(order: int) -> Dict[str, int]:
        return {"total_packets": order}

    @staticmethod
    def total_bytes(order: int) -> Dict[str, int]:
        return {"total_bytes": order}

    @staticmethod
    def timestamp(order: int) -> Dict[str, int]:
        return {"timestamp": order}


class PipelineBuilder:
    """Pipeline Builder with modular and reusable components."""

    def __init__(self, collection: Collection):
        self.collection = collection
        self.pipeline = []

    def build(self) -> List[Dict[str, Any]]:
        """Return the constructed pipeline."""
        return self.pipeline

    def new(self) -> "PipelineBuilder":
        """Reset the pipeline."""
        self.pipeline = []
        return self

    def add_stage(self, stage: Dict[str, Any]) -> "PipelineBuilder":
        """Add a custom stage to the pipeline."""
        self.pipeline.append(stage)
        return self

    # Generic MongoDB Stages
    def match(self, criteria: Dict[str, Any]) -> "PipelineBuilder":
        """Add a $match stage."""
        self.add_stage({"$match": criteria})
        return self

    def group(self, group_fields: Dict[str, Any]) -> "PipelineBuilder":
        """Add a $group stage."""
        self.add_stage({"$group": group_fields})
        return self

    def project(self, projection: Dict[str, Any]) -> "PipelineBuilder":
        """Add a $project stage."""
        self.add_stage({"$project": projection})
        return self

    def sort(self, sort_fields: Dict[str, int]) -> "PipelineBuilder":
        """Add a $sort stage."""
        self.add_stage({"$sort": sort_fields})
        return self

    def unwind(self, field: str) -> "PipelineBuilder":
        """Add a $unwind stage."""
        self.add_stage({"$unwind": field})
        return self

    def count_and_paginate(self, page: int, page_size: int) -> "PipelineBuilder":
        """Combine count and pagination in one $facet stage"""
        # I tried different ways to separate pagination and count, but it will introduce way more complexity, so I decided to keep it as this
        skip = (page - 1) * page_size
        self.add_stage(
            {
                "$facet": {
                    "metadata": [{"$count": "total_documents"}],
                    "data": [{"$skip": skip}, {"$limit": page_size}],
                }
            }
        )
        return self

    def limit(self, limit: int) -> "PipelineBuilder":
        """Add a $limit stage."""
        self.add_stage({"$limit": limit})
        return self

    def skip(self, skip: int) -> "PipelineBuilder":
        """Add a $skip stage."""
        self.add_stage({"$skip": skip})
        return self

    def facet(self, facets: Dict[str, List[Dict[str, Any]]]) -> "PipelineBuilder":
        """Add a $facet stage."""
        self.add_stage({"$facet": facets})
        return self

    def paginate(self, page: int, page_size: int) -> "PipelineBuilder":
        """Add pagination stages."""
        return self.skip((page - 1) * page_size).limit(page_size)


class TimeRangeBuilder:
    """Helper for time range-related pipeline operations."""

    @staticmethod
    def match_time_range(start_time: float, end_time: float) -> Dict[str, Any]:
        """Create a $match stage for time range."""
        return {"timestamp": {"$gte": start_time, "$lte": end_time}}


class ProtocolAnalysisBuilder:
    """Pipeline for Protocol Analysis DTO."""

    @staticmethod
    def protocol_distribution() -> List[Dict[str, Any]]:
        """Pipeline for protocol distribution."""
        return [
            {
                "$group": {
                    "_id": "$protocol",
                    "packet_count": {"$sum": 1},
                    "total_bytes": {"$sum": "$length"},
                }
            },
            {
                "$project": {
                    "protocol": "$_id",
                    "percentage_count": {
                        "$multiply": [{"$divide": ["$packet_count", "$$total"]}, 100]
                    },
                    "percentage_bytes": {
                        "$multiply": [
                            {"$divide": ["$total_bytes", "$$total_bytes"]},
                            100,
                        ]
                    },
                    "packet_count": 1,
                    "total_bytes": 1,
                    "_id": 0,
                }
            },
        ]


class NetworkStatsBuilder:
    """Pipeline for NetworkStats DTO."""

    @staticmethod
    def network_stats() -> List[Dict[str, Any]]:
        """Pipeline for calculating network statistics."""
        return [
            {
                "$group": {
                    "_id": None,
                    "total_packets": {"$sum": 1},
                    "total_bytes": {"$sum": "$length"},
                    "avg_packet_size": {
                        "$avg": {"$divide": ["$length", "$total_packets"]}
                    },
                }
            },
            {
                "$project": {
                    "total_packets": 1,
                    "total_bytes": 1,
                    "avg_packet_size": 1,
                    "_id": 0,
                }
            },
        ]
