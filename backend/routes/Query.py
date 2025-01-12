from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from packet.Packet import ProcessedPacket
from db.Crud import (
    get_packets_by_time_range,
    get_packets_by_protocol,
    get_packets_by_source_ip,
)

router = APIRouter(prefix="/query", tags=["query"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.get("/time", response_model=List[ProcessedPacket])
async def query_by_time(
    start_time: float,
    end_time: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    按时间段查询数据包
    Args:
        start_time: 开始时间 (unix timestamp)
        end_time: 结束时间 (unix timestamp)
        page: 页码
        page_size: 每页数量
        token: 认证token
    Returns:
        时间段内的数据包列表
    """
    return await get_packets_by_time_range(start_time, end_time, page, page_size)


@router.get("/protocol", response_model=List[ProcessedPacket])
async def query_by_protocol(
    protocol: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    按协议类型查询数据包
    Args:
        protocol: 协议类型 (TCP/UDP/ICMP)
        page: 页码
        page_size: 每页数量
        token: 认证token
    Returns:
        匹配协议类型的数据包列表
    """
    return await get_packets_by_protocol(protocol, page, page_size)


@router.get("/source-ip", response_model=List[ProcessedPacket])
async def query_by_source_ip(
    ip_address: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    按源IP地址查询数据包
    Args:
        ip_address: 源IP地址
        page: 页码
        page_size: 每页数量
        token: 认证token
    Returns:
        匹配源IP地址的数据包列表
    """
    return await get_packets_by_source_ip(ip_address, page, page_size)
