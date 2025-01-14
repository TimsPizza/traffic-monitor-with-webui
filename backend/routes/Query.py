from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from models.Dtos import (
    FullPacket,
    NetworkStats,
    ProtocolAnalysis,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
)
from db.CrudService import CrudService

router = APIRouter(prefix="/query", tags=["query"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

crud_service = CrudService()

@router.get("/time", response_model=List[FullPacket])
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
    return crud_service.find_packets_by_timerange(start_time, end_time, page, page_size)

@router.get("/protocol", response_model=List[FullPacket])
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
    return crud_service.find_packets_by_protocol(protocol, page, page_size)

@router.get("/source-ip", response_model=List[FullPacket])
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
    return crud_service.find_packets_by_ip(ip_address, page, page_size)

@router.get("/network-stats", response_model=NetworkStats)
async def get_network_stats(
    start_time: float,
    end_time: float,
    token: str = Depends(oauth2_scheme),
):
    """
    获取网络统计信息
    Args:
        start_time: 开始时间 (unix timestamp)
        end_time: 结束时间 (unix timestamp)
        token: 认证token
    Returns:
        网络统计信息
    """
    return crud_service.get_network_stats(start_time, end_time)

@router.get("/protocol-analysis", response_model=ProtocolAnalysis)
async def get_protocol_analysis(
    start_time: float,
    end_time: float,
    token: str = Depends(oauth2_scheme),
):
    """
    获取协议分析信息
    Args:
        start_time: 开始时间 (unix timestamp)
        end_time: 结束时间 (unix timestamp)
        token: 认证token
    Returns:
        协议分析信息
    """
    return crud_service.get_protocol_analysis(start_time, end_time)

@router.get("/top-source-ips", response_model=List[TopSourceIP])
async def get_top_source_ips(
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
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
    return crud_service.get_top_source_ips(limit)

@router.get("/protocol-distribution", response_model=ProtocolDistribution)
async def get_protocol_distribution(
    start_time: float,
    end_time: float,
    token: str = Depends(oauth2_scheme),
):
    """
    获取协议分布信息
    Args:
        start_time: 开始时间 (unix timestamp)
        end_time: 结束时间 (unix timestamp)
        token: 认证token
    Returns:
        协议分布信息
    """
    return crud_service.get_protocol_distribution(start_time, end_time)

@router.get("/traffic-summary", response_model=TrafficSummary)
async def get_traffic_summary(
    start_time: float,
    end_time: float,
    token: str = Depends(oauth2_scheme),
):
    """
    获取流量摘要信息
    Args:
        start_time: 开始时间 (unix timestamp)
        end_time: 结束时间 (unix timestamp)
        token: 认证token
    Returns:
        流量摘要信息
    """
    return crud_service.get_traffic_summary(start_time, end_time)

@router.get("/time-series", response_model=TimeSeriesData)
async def get_time_series_data(
    start_time: float,
    end_time: float,
    interval: int = Query(60, ge=1, description="时间间隔（秒）"),
    token: str = Depends(oauth2_scheme),
):
    """
    获取时间序列数据
    Args:
        start_time: 开始时间 (unix timestamp)
        end_time: 结束时间 (unix timestamp)
        interval: 时间间隔（秒）
        token: 认证token
    Returns:
        时间序列数据
    """
    return crud_service.get_time_series_data(start_time, end_time, interval)
