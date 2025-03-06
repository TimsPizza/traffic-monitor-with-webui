from typing import Optional
from fastapi import APIRouter, Depends

from packet.PacketAnalyzer import PacketAnalyzer, AnalyzerSingleton
from service.CaptureService import CaptureService
from core.config import oauth2_scheme

router = APIRouter(prefix="/capture", tags=["capture"])
capture_service = CaptureService()


def get_packet_analyzer() -> PacketAnalyzer:
    return AnalyzerSingleton.get_instance()


@router.post("/start")
async def start_capture(
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """启动抓包分析 (Start packet capture)"""
    if not capture_service.start_capture():
        return {"status": "failed", "message": "Failed to start capture"}
    return {"status": "success", "message": "Capture started"}


@router.post("/stop")
async def stop_capture(
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """停止抓包分析 (Stop packet capture)"""
    if not capture_service.stop_capture():
        return {"status": "failed", "message": "Failed to stop capture"}
    return {"status": "success", "message": "Capture stopped"}


@router.get("/status")
async def get_capture_status(
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
    token: str = Depends(oauth2_scheme),
):
    """获取抓包状态 (Get capture status)"""
    return {"status": "running" if capture_service.is_capturing() else "stopped"}
