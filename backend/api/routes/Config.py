from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from api.routes.Capture import get_packet_analyzer
from models.Dtos import (
    FilterAll,
    NetworkInterfacePost,
    NetworkInterfaces,
    ProtocolPortMappingRuleRecord,
    ProtocolPortMappingRulesAll,
)
from service.ConfigService import CONFIG_SERVICE, ConfigService
from models.Filter import CaptureFilterRecord
from packet.PacketAnalyzer import PacketAnalyzer, AnalyzerSingleton
from core.config import oauth2_scheme

router = APIRouter(prefix="/config", tags=["settings"])


@router.get("/filter", response_model=List[CaptureFilterRecord])
async def get_all_filter(
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """获取所有过滤器规则 (Get all filter rules)"""
    resp = CONFIG_SERVICE.get_all_filter()
    return resp.filters


@router.post("/filter", response_model=List[CaptureFilterRecord])
async def set_filter(
    filter_records: List[CaptureFilterRecord],
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """设置新的过滤器规则 (Set new filter rules)"""
    result = CONFIG_SERVICE.add_filter(filter_records)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to set filters")
    return result


@router.get("/rules", response_model=ProtocolPortMappingRulesAll)
async def get_all_protocol_port_mapping_rules(
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """获取所有端口映射规则 (Get all port mapping rules)"""
    return CONFIG_SERVICE.get_all_protocol_port_mapping_rules()


@router.post("/rules", response_model=ProtocolPortMappingRulesAll)
async def update_protocol_port_mapping_rule(
    rule: ProtocolPortMappingRuleRecord,
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """添加端口映射规则 (Update port mapping rule)"""
    if not CONFIG_SERVICE.add_rule(rule):
        raise HTTPException(status_code=400, detail="Failed to update rule")
    return CONFIG_SERVICE.get_all_protocol_port_mapping_rules()


@router.delete("/rules", response_model=ProtocolPortMappingRulesAll)
async def remove_protocol_port_mapping_rule(
    rule: ProtocolPortMappingRuleRecord,
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """移除端口映射规则 (Remove port mapping rule)"""
    if not CONFIG_SERVICE.remove_rule(rule):
        raise HTTPException(status_code=400, detail="Failed to remove rule")
    return CONFIG_SERVICE.get_all_protocol_port_mapping_rules()


@router.get("/interfaces", response_model=NetworkInterfaces)
async def get_all_net_interfaces(
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """获取所有网络接口 (Get all network interfaces)"""
    return CONFIG_SERVICE.get_all_net_interfaces()


@router.post("/interfaces", response_model=str)
async def set_net_interface(
    request: NetworkInterfacePost,
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """设置网络接口 (Set network interface)"""
    if not CONFIG_SERVICE.set_net_interface(request.interface):
        raise HTTPException(status_code=400, detail="Failed to set interface")
    return request.interface
