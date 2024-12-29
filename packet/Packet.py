from dataclasses import dataclass


@dataclass
class CapturedPacket:
    def __init__(self, packet: bytes, timestamp: float):
        self.packet = packet
        self.timestamp = timestamp
