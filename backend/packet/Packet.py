from dataclasses import dataclass

from pydantic import BaseModel


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


class ProcessedPacket(BaseModel):
    _id: str = ""  # mongo object id must be '_id'
    timestamp: float = -1
    layer: str = ""
    source_ip: str = ""
    src_port: int = -1
    src_region: str = ""
    dst_port: int = -1
    protocol: str = ""
    length: int = -1
    is_handshake: bool = False
