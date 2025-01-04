from dataclasses import dataclass
from enum import Enum, auto


class Layer(Enum):
    PHYSICAL = "Physical"
    DATALINK = "Data Link"
    NETWORK = "Network"
    TRANSPORT = "Transport"
    APPLICATION = "Application"

    def __str__(self):
        return self.value


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
