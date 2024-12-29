from pydantic import BaseModel, IPvAnyAddress, Field
from typing import Annotated, Optional, List
from enum import Enum


class PortRangeInt(BaseModel):
    port: Annotated[int, Field(ge=1, le=65535)]  # ge: >=1, le: <=65535


class Protocol(str, Enum):
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"


class CaptureFilterRecord(BaseModel):
    src_ip: Optional[IPvAnyAddress] = None
    dst_ip: Optional[IPvAnyAddress] = None
    src_port: Optional[PortRangeInt] = None
    dst_port: Optional[PortRangeInt] = None
    protocol: Optional[Protocol] = None
