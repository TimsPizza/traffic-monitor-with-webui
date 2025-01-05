from dataclasses import dataclass


class Layer:
    PHYSICAL = "Physical"
    DATALINK = "Data Link"
    NETWORK = "Network"
    TRANSPORT = "Transport"
    APPLICATION = "Application"


@dataclass
class CapturedPacket:
    raw_packet: bytes
    timestamp: float


@dataclass
class ProcessedPacket:
    timestamp: float = -1
    layer: str = ""
    source_ip: str = ""
    src_port: int = -1
    dst_port: int = -1
    protocol: str = ""
    length: int = -1
