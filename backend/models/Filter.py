from typing import Annotated, Optional, Union
from enum import Enum


from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ValidationError
import ipaddress


class CIDRString(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema

        return core_schema.no_info_after_validator_function(
            cls.validate_cidr,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )

    @staticmethod
    def validate_cidr(value: str) -> str:
        try:
            ipaddress.ip_network(value, strict=False)
            return value
        except ValueError as e:
            raise ValueError(f"Invalid CIDR: {value}") from e


IPOrCIDR = Union[ipaddress.IPv4Address, ipaddress.IPv6Address, CIDRString]


class PortRangeInt(BaseModel):
    port: Annotated[int, Field(ge=1, le=65535)]  # ge: >=1, le: <=65535


class Protocol(str, Enum):
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"


class CaptureFilterRecord(BaseModel):
    src_ip: Optional[IPOrCIDR] = None
    dst_ip: Optional[IPOrCIDR] = None
    src_port: Optional[List[int]] = None
    dst_port: Optional[List[int]] = None
    protocol: Optional[Protocol] = None

    @field_validator("src_port", "dst_port", mode="before")
    def validate_ports(cls, value):
        if value is None:
            return None
        for port in value:
            if not (1 <= port <= 65535):
                raise ValueError(f"Port {port} is out of range (1-65535)")
        return value

    @field_validator("src_ip", "dst_ip", mode="before")
    def parse_ip_or_cidr(cls, value):
        if value is None:
            return None
        try:
            return ipaddress.ip_address(value)
        except ValueError:
            try:
                return CIDRString.validate_cidr(value)
            except ValueError as e:
                raise ValueError(f"Invalid IP or CIDR: {value}") from e
