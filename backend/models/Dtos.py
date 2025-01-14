from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Dict, Tuple


class FullPacket(BaseModel):
    id: str
    region: str = ""
    src_ip: str = ""
    src_port: int = -1
    dst_port: int = -1
    protocol: str = ""
    timestamp: float = -1


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


class ProtocolDistribution(BaseModel):
    """Protocol distribution analysis DTO"""

    protocol: str
    percentage: float  # 0.0 - 100.0
    packet_count: int
    total_bytes: int


class NetworkStats(BaseModel):
    """Network statistics DTO"""

    total_packets: int = -1
    total_bytes: int = -1
    avg_packet_size: float = -1
    protocol_distribution: List[ProtocolDistribution] = []


class ProtocolAnalysis(BaseModel):
    """Protocol analysis DTO"""

    protocol: str
    packet_count: int
    source_ips: List[str]
    ports: List[int]
    avg_packet_size: float
    time_range: TimeRange  # [start, end]


class TopSourceIP(BaseModel):
    """Top source IP analysis DTO"""

    ip: str
    packet_count: int
    total_bytes: int
    protocols: Dict[str, int]  # protocol: count


class TrafficSummary(BaseModel):
    """Comprehensive traffic summary DTO"""

    total_packets: int
    total_bytes: int
    top_source_ips: List[TopSourceIP]
    protocol_distribution: List[ProtocolDistribution]
    time_range: TimeRange


class TimeSeriesData(BaseModel):
    """Time series analysis DTO"""

    packet_count: int
    total_bytes: int
    protocol_distribution: List[ProtocolDistribution]  # protocol distributions
    time_range: TimeRange
