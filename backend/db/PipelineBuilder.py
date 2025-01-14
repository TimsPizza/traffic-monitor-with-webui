from typing import Dict, List, Any
from pymongo.collection import Collection


class PipelineBuilder:
    """Main pipeline builder with mixin pattern for modular query building"""

    def __init__(self, collection: Collection):
        self.collection = collection
        self.pipeline = []

    # Core pipeline operations
    def build(self) -> List[Dict[str, Any]]:
        """Return the built pipeline"""
        return self.pipeline

    def reset(self) -> "PipelineBuilder":
        """Reset the pipeline"""
        self.pipeline = []
        return self

    def project(self, fields: Dict[str, Any]) -> "PipelineBuilder":
        """Add projection stage to pipeline"""
        self.pipeline.append({"$project": fields})
        return self

    def sort(self, field: str, order: int = -1) -> "PipelineBuilder":
        """Add sorting stage to pipeline"""
        self.pipeline.append({"$sort": {field: order}})
        return self

    def limit(self, limit: int) -> "PipelineBuilder":
        """Add limit stage to pipeline"""
        self.pipeline.append({"$limit": limit})
        return self

    def unwind(self, field: str) -> "PipelineBuilder":
        """Add unwind stage to pipeline"""
        self.pipeline.append({"$unwind": f"${field}"})
        return self

    def paginate(self, page: int, page_size: int) -> "PipelineBuilder":
        """Add pagination stages to pipeline"""
        skip = (page - 1) * page_size
        self.pipeline.extend([{"$skip": skip}, {"$limit": page_size}])
        return self

    # Time range operations
    def match_time_range(self, start_time: float, end_time: float) -> "PipelineBuilder":
        """Add time range filter to pipeline"""
        self.pipeline.append(
            {"$match": {"timestamp": {"$gte": start_time, "$lte": end_time}}}
        )
        return self

    # Protocol operations
    def match_protocol(self, protocol: str) -> "PipelineBuilder":
        """Add protocol filter to pipeline"""
        self.pipeline.append({"$match": {"protocol": protocol}})
        return self

    def group_by_protocol(self) -> "PipelineBuilder":
        """Add protocol grouping to pipeline"""
        self.pipeline.append(
            {
                "$group": {
                    "_id": "$protocol",
                    "count": {"$sum": 1},
                    "total_bytes": {"$sum": "$length"},
                    "total_packets": {"$sum": 1},
                    "source_ips": {"$addToSet": "$source_ip"},
                }
            }
        )
        return self.project(
            {
                "protocol": "$_id",
                "total_bytes": 1,
                "total_packets": 1,
                "source_ips": 1,
                "_id": 0,
            }
        )

    # Source IP operations
    def match_source_ip(self, ip_address: str) -> "PipelineBuilder":
        """Add source IP filter to pipeline"""
        self.pipeline.append({"$match": {"source_ip": ip_address}})
        return self

    def group_by_source_ip(self) -> "PipelineBuilder":
        """Add source IP grouping to pipeline"""
        self.pipeline.append(
            {
                "$group": {
                    "_id": "$source_ip",
                    "count": {"$sum": 1},
                    "total_bytes": {"$sum": "$length"},
                    "region": {"$first": "$src_region"},
                }
            }
        )
        return self.project(
            {
                "source_ip": "$_id",
                "total_packets": "$count",
                "total_bytes": 1,
                "region": 1,
                "_id": 0,
            }
        )

    # Time interval operations
    def group_by_time_interval(self, interval: int) -> "PipelineBuilder":
        """Add time interval grouping to pipeline"""
        self.pipeline.append(
            {
                "$group": {
                    "_id": {
                        "$subtract": ["$timestamp", {"$mod": ["$timestamp", interval]}]
                    },
                    "total_packets": {"$sum": 1},
                    "total_bytes": {"$sum": "$length"},
                }
            }
        )
        return self.project(
            {
                "start_time": "$_id",
                "timestamp": "$_id",
                "total_packets": 1,
                "total_bytes": 1,
                "_id": 0,
            }
        )

    # Traffic summary operations
    def group_traffic_summary(self) -> "PipelineBuilder":
        """Add traffic summary grouping to pipeline"""
        self.pipeline.append(
            {
                "$group": {
                    "_id": None,
                    "total_packets": {"$sum": 1},
                    "total_bytes": {"$sum": "$length"},
                    "unique_ips": {"$addToSet": "$source_ip"},
                    "protocols": {"$addToSet": "$protocol"},
                }
            }
        )
        return self
