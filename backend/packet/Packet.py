from dataclasses import dataclass


@dataclass
class CapturedPacket:
    packet: bytes
    timestamp: float


@dataclass
class ProcessedPacket:
    timestamp: float
    source_ip: str
    source_port: int
    destination_port: int
    protocol: str
