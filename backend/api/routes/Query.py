from typing import List, Callable, TypeVar, Any
from functools import wraps
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from models.Dtos import (
    FullPacket,
    NetworkStats,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
    PaginatedResponse,
)
from service.CrudService import CrudService

router = APIRouter(prefix="/query", tags=["query"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

crud_service = CrudService()

T = TypeVar("T")


@router.get("/time", response_model=PaginatedResponse[FullPacket])
async def query_by_time(
    start: float,
    end: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    按时间段查询数据包
    Args:
        start: 开始时间 (unix timestamp)
        end: 结束时间 (unix timestamp)
        page: 页码
        page_size: 每页数量
        token: 认证token
    Returns:
        时间段内的数据包列表
    """
    return crud_service.find_packets_by_timerange(start, end, page, page_size)


@router.get("/protocol", response_model=PaginatedResponse[FullPacket])
async def query_by_protocol(
    protocol: str,
    start: float,
    end: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
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
    return crud_service.find_packets_by_protocol(protocol, start, end, page, page_size)


@router.get("/source-ip", response_model=PaginatedResponse[FullPacket])
async def query_by_source_ip(
    ip_address: str,
    start: float,
    end: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
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
    return crud_service.find_packets_by_ip(ip_address, start, end, page, page_size)


@router.get("/top-source-ips", response_model=PaginatedResponse[TopSourceIP])
async def get_top_source_ips(
    start: float,
    end: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    获取流量最大的源IP地址
    Args:
        limit: 返回的IP数量
        token: 认证token
    Returns:
        流量最大的源IP地址列表
    """
    return crud_service.get_top_source_ips(start, end, page, page_size)


@router.get(
    "/protocol-distribution", response_model=PaginatedResponse[ProtocolDistribution]
)
async def get_protocol_distribution(
    start: float,
    end: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    获取协议分布信息
    Args:
        start: 开始时间 (unix timestamp)
        end: 结束时间 (unix timestamp)
        token: 认证token
    Returns:
        协议分布信息
    """
    return crud_service.get_protocol_distribution(start, end, page, page_size)


@router.get("/traffic-summary", response_model=PaginatedResponse[TrafficSummary])
async def get_traffic_summary(
    start: float,
    end: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    获取流量摘要信息
    Args:
        start: 开始时间 (unix timestamp)
        end: 结束时间 (unix timestamp)
        token: 认证token
    Returns:
        流量摘要信息
    """
    return crud_service.get_traffic_summary(start, end, page, page_size)


@router.get("/time-series", response_model=PaginatedResponse[TimeSeriesData])
async def get_time_series_data(
    start: float,
    end: float,
    interval: int = Query(60, ge=1, description="时间间隔（秒）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    获取时间序列数据
    Args:
        start: 开始时间 (unix timestamp)
        end: 结束时间 (unix timestamp)
        interval: 时间间隔（秒）
        token: 认证token
    Returns:
        时间序列数据
    """
    return crud_service.get_time_series_data(start, end, interval, page, page_size)


@router.get("/port", response_model=PaginatedResponse[FullPacket])
async def query_by_port(
    port: int,
    start: float,
    end: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    按端口号查询数据包
    Args:
        port: 目标端口号
        start: 开始时间 (unix timestamp)
        end: 结束时间 (unix timestamp)
        page: 页码
        page_size: 每页数量
        token: 认证token
    Returns:
        匹配端口号的数据包列表
    """
    return crud_service.find_packets_by_port(port, start, end, page, page_size)


@router.get("/region", response_model=PaginatedResponse[FullPacket])
async def query_by_region(
    region: str,
    start: float,
    end: float,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    token: str = Depends(oauth2_scheme),
):
    """
    按地区查询数据包
    Args:
        region: 地区名称
        start: 开始时间 (unix timestamp)
        end: 结束时间 (unix timestamp)
        page: 页码
        page_size: 每页数量
        token: 认证token
    Returns:
        匹配地区的数据包列表
    """
    return crud_service.find_packets_by_region(region, start, end, page, page_size)
