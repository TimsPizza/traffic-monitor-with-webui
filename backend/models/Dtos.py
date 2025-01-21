from pydantic import BaseModel, field_validator, model_validator
from typing import Any, Optional, List, Dict, Tuple, Union, Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response DTO"""

    total: int
    page: int
    page_size: int
    data: Union[List[T], T]


class FullPacket(BaseModel):
    id: str | int
    src_region: str = ""
    src_ip: str = ""
    dst_port: int = -1
    protocol: str = ""
    timestamp: float = -1
    length: int = -1


class TimeRange(BaseModel):
    start: float
    end: float

    @field_validator("start", "end")
    def validate_positive(cls, value: float, info) -> float:
        if value < 0:
            raise ValueError(f"{info.field_name} must be a positive number")
        return value

    @model_validator(mode="after")
    def validate_time_range(self) -> "TimeRange":
        if self.start >= self.end:
            raise ValueError("Start time must be less than end time")
        return self


class BasicPacket(BaseModel):
    """Basic packet information"""

    src_ip: str
    dst_ip: str
    timestamp: float


class ProtocolDistributionItem(BaseModel):
    """Protocol distribution analysis DTO"""

    protocol: str
    percentage_count: float  # 0.0 - 100.0
    percentage_bytes: float  # 0.0 - 100.0
    packet_count: int
    total_bytes: int


class ProtocolDistribution(BaseModel):
    distribution: List[ProtocolDistributionItem] = []
    time_range: TimeRange = None


class NetworkStats(BaseModel):
    """Network statistics DTO"""

    total_packets: int = -1
    total_bytes: int = -1
    avg_packet_size: float = -1
    protocol_distribution: ProtocolDistribution


class TopSourceIP(BaseModel):
    """Top source IP analysis DTO"""

    ip: str
    src_region: str
    percentage_packets: float
    percentage_bytes: float
    total_packets: int
    total_bytes: int


class TrafficSummary(BaseModel):
    """Comprehensive traffic summary DTO"""

    total_packets: int = -1
    total_bytes: int = -1
    top_source_ips: List[TopSourceIP] = []
    protocol_distribution: ProtocolDistribution = None
    time_range: TimeRange = None


class TimeSeriesData(BaseModel):
    """Time series analysis DTO"""

    total_packets: int
    total_bytes: int
    time_range: TimeRange
