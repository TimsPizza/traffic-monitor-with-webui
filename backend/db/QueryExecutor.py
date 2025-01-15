import logging
from typing import List, Dict, Any, Type
from pymongo.collection import Collection
from .PipelineBuilder import PipelineBuilder
from models.Dtos import (
    FullPacket,
    NetworkStats,
    ProtocolAnalysis,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
)


class QueryExecutor:
    def __init__(self, collection: Collection):
        self.collection = collection
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pipeline_builder = PipelineBuilder(collection)

    def execute_pipeline(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a MongoDB aggregation pipeline"""
        try:
            return list(self.collection.aggregate(pipeline))
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
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .match_source_ip(ip_address)
                .sort("timestamp", -1)
                .paginate(page, page_size)
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error finding packets by IP: {e}")
            return []

    def find_packets_by_protocol(
        self, protocol: str, page: int = 1, page_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Find packets by protocol with pagination"""
        try:
            pipeline = (
                self.pipeline_builder.reset()
                .match_protocol(protocol)
                .sort("timestamp", -1)
                .paginate(page, page_size)
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
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .sort("timestamp", -1)
                .paginate(page, page_size)
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
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .rename_field("src_region", "region")
                .match_port(port)
                .sort("timestamp", -1)
                .paginate(page, page_size)
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
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .rename_field("src_region", "region")
                .match_region(region)
                .sort("timestamp", -1)
                .paginate(page, page_size)
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
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .group_by_protocol()
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return {}

    def get_protocol_distribution(
        self, start_time: float, end_time: float
    ) -> List[Dict[str, Any]]:
        """Get protocol distribution for a given time range"""
        try:
            pipeline = (
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .group_by_protocol()
                .sort("total_packets", -1)
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error getting protocol distribution: {e}")
            return []

    def get_top_source_ips(
        self, start_time: float, end_time: float, page: int, page_size: int
    ) -> List[Dict[str, Any]]:
        """Get top source IPs by packet count"""
        try:
            pipeline = (
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .group_by_source_ip()
                .sort("total_packets", -1)
                .paginate(page, page_size)
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error getting top source IPs: {e}")
            return []

    def get_time_series_data(
        self, start_time: float, end_time: float, interval: int
    ) -> List[Dict[str, Any]]:
        """Get time series data for a given time range and interval"""
        try:
            pipeline = (
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .group_by_time_interval(interval)
                .sort("timestamp", 1)
                .build()
            )

            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error getting time series data: {e}")
            return {}

    def get_traffic_summary(
        self, start_time: float, end_time: float
    ) -> List[Dict[str, Any]]:
        """Get traffic summary for a given time range"""
        try:
            pipeline = (
                self.pipeline_builder.reset()
                .match_time_range(start_time, end_time)
                .group_traffic_summary()
                .build()
            )
            return self.execute_pipeline(pipeline)
        except Exception as e:
            self.logger.error(f"Error getting traffic summary: {e}")
            return {}
