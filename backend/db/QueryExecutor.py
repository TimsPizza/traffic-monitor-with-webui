import logging
from typing import List, Dict, Any, Type
from pymongo.collection import Collection
from .PipelineBuilder import (
    GroupBy,
    MatchBy,
    PipelineBuilder,
    ProjectBy,
    SortBy,
    TimeRangeBuilder,
)
from models.Dtos import (
    FullPacket,
    NetworkStats,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
)


class QueryExecutor:
    def __init__(self, collection: Collection):
        self.collection = collection
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pipeline_builder = PipelineBuilder(collection=collection)

    def execute_pipeline(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a MongoDB aggregation pipeline"""
        try:
            res = list(self.collection.aggregate(pipeline))
            if len(res) == 0:
                return []
            return res[0]
        except Exception as e:
            self.logger.error(f"Error executing pipeline: {e}")
            return []

    def find_packets_by_ip(
        self,
        ip_address: str,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find packets by source IP with pagination"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .match(MatchBy.source_ip(ip_address))
                .sort(SortBy.timestamp(-1))
                .count_and_paginate(page, page_size)
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error finding packets by IP: {e}")
            return []

    def find_packets_by_protocol(
        self,
        protocol: str,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find packets by protocol with pagination"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .match(MatchBy.protocol(protocol))
                .sort(SortBy.timestamp(-1))
                .count_and_paginate(page, page_size)
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error finding packets by protocol: {e}")
            return []

    def find_packets_by_time_range(
        self, start_time: float, end_time: float, page: int = 1, page_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Find packets by time range with pagination"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .sort(SortBy.timestamp(-1))
                .count_and_paginate(page, page_size)
                .build()
            )

            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error finding packets by time range: {e}")
            return []

    def find_packets_by_port(
        self,
        port: int,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find packets by destination port with pagination"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .match(MatchBy.port(port))
                .sort(SortBy.timestamp(-1))
                .count_and_paginate(page, page_size)
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error finding packets by port: {e}")
            return []

    def find_packets_by_region(
        self,
        region: str,
        start_time: float,
        end_time: float,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find packets by region with pagination"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .match(MatchBy.region(region))
                .sort(SortBy.timestamp(-1))
                .count_and_paginate(page, page_size)
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error finding packets by region: {e}")
            return []

    def get_network_stats(
        self, start_time: float, end_time: float
    ) -> List[Dict[str, Any]]:
        """Get network statistics for a given time range"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .group(GroupBy.protocol())
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return {}

    def get_protocol_distribution(
        self, start_time: float, end_time: float, page: int, page_size: int
    ) -> Dict[str, Any]:
        """Get protocol distribution for a given time range with pagination and total count"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .group(GroupBy.protocol())
                .project(ProjectBy.protocol())
                .sort(SortBy.total_packets(-1))
                .count_and_paginate(page, page_size)
                .build()
            )

            result = self.execute_pipeline(pipeline)
            return result
        except Exception as e:
            self.logger.error(f"Error getting protocol distribution: {e}")
            return []

    def get_top_source_ips(
        self, start_time: float, end_time: float, page: int, page_size: int
    ) -> Dict[str, Any]:
        """Get top source IPs by packet count with pagination and total count"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .group(GroupBy.top_source_ips())
                .project(ProjectBy.top_source_ips())
                .sort(SortBy.total_bytes(-1))
                .count_and_paginate(page, page_size)
                .build()
            )

            result = self.execute_pipeline(pipeline)
            return result
        except Exception as e:
            self.logger.error(f"Error getting top source IPs: {e}")
            return []

    def get_time_series_data(
        self,
        start_time: float,
        end_time: float,
        interval: int,
        page: int,
        page_size: int,
    ) -> List[Dict[str, Any]]:
        """Get time series data for a given time range and interval"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .group(GroupBy.time_interval(interval))
                .project(ProjectBy.time_interval(interval))
                .sort(SortBy.timestamp(-1))
                .count_and_paginate(page, page_size)
                .build()
            )

            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error getting time series data: {e}")
            return {}

    def get_traffic_summary(
        self, start_time: float, end_time: float, page: int, page_size: int
    ) -> List[Dict[str, Any]]:
        """Get traffic summary for a given time range"""
        try:
            pipeline = (
                self.pipeline_builder.new()
                .match(MatchBy.time_range(start_time, end_time))
                .group(GroupBy.traffic_summary())
                .project(ProjectBy.traffic_summary())
                .count_and_paginate(page, page_size)
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error getting traffic summary: {e}")
            return {}
