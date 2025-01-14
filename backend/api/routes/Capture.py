from typing import List
from fastapi import APIRouter, Depends

from models import CaptureFilterRecord
from packet.PacketAnalyzer import PacketAnalyzer, AnalyzerSingleton
from packet.utils.BpfUtils import BPFUtils

# TODO: add auth to this route
router = APIRouter(prefix="/capture")


def get_packet_analyzer():
    return AnalyzerSingleton.get_instance()


@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.post("/start")
async def start_capture(
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
):
    if analyzer.is_running:
        return {"status": "Capture already started"}
    analyzer.start()
    return {"status": "Capture started"}


@router.post("/stop")
async def stop_capture(analyzer: PacketAnalyzer = Depends(get_packet_analyzer)):
    if not analyzer.is_running:
        return {"status": "Capture already stopped"}
    analyzer.stop()
    return {"status": "Capture stopped"}


@router.get("/config/filter", response_model=List[CaptureFilterRecord])
async def get_all_filter(analyzer: PacketAnalyzer = Depends(get_packet_analyzer)):
    filter = analyzer._packet_producer.filter
    if not filter:
        return []
    resp = BPFUtils.parse_filter_expression(filter)
    return resp


@router.post("/config/filter", response_model=List[CaptureFilterRecord])
async def set_filter(
    filter_records: List[CaptureFilterRecord],
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
):
    filter = BPFUtils.build_filter_expression(filter_records)
    analyzer._packet_producer.apply_filter(filter)
    return filter_records


@router.get("/status")
async def get_status(analyzer: PacketAnalyzer = Depends(get_packet_analyzer)):
    return {
        "running": analyzer.is_running,
        "metrics": {
            "consumer": analyzer._packet_consumer._metrics,
            "queue": analyzer._double_buffer_queue.metrics,
        },
    }
