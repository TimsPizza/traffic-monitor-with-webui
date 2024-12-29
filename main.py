from hmac import new
import signal
from typing import List
import uvicorn
from fastapi import Depends, FastAPI, BackgroundTasks
from fastapi.logger import logger
from contextlib import asynccontextmanager
from scapy.all import Ether, IP, TCP
import os
import sys

from models import CaptureFilterRecord
from packet import PacketAnalyzer
from utils import BPFUtils


@asynccontextmanager
async def life_span(app: FastAPI):
    logger.info("Starting")
    yield
    logger.info("Stopping")


app = FastAPI(lifespan=life_span)


def get_packet_analyzer():
    analyzer = PacketAnalyzer(
        buffer_min_size=256,
        buffer_max_size=8192,
        consumer_max_workers=4,
        consumer_batch_size=256,
        capture_interface="eth0",
    )
    try:
        yield analyzer
    finally:
        if analyzer.is_running:
            analyzer.stop()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/start_capture")
async def start_capture(
    background_tasks: BackgroundTasks,
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
):
    async def start_analysis():
        analyzer.start()

    background_tasks.add_task(start_analysis)
    return {"status": "Capture started"}


@app.get("/capture/config/filter", response_model=List[CaptureFilterRecord])
async def get_all_filter(analyzer: PacketAnalyzer = Depends(get_packet_analyzer)):
    filter = analyzer._packet_producer._filter
    if not filter:
        return []
    resp = BPFUtils.parse_filter_expression(filter)
    return resp


@app.post("/capture/config/filter", response_model=List[CaptureFilterRecord])
async def set_filter(
    filter_records: List[CaptureFilterRecord],
    analyzer: PacketAnalyzer = Depends(get_packet_analyzer),
):
    filter = BPFUtils.build_filter_expression(filter_records)
    analyzer._packet_producer.apply_filter(filter)
    return filter_records


@app.get("/status")
async def get_status(analyzer: PacketAnalyzer = Depends(get_packet_analyzer)):
    return {
        "running": analyzer.is_running,
        "metrics": {
            "consumer": analyzer._packet_consumer._metrics,
            "producer": analyzer._packet_producer._metrics,
        },
    }


@app.post("/stop")
async def stop_capture(analyzer: PacketAnalyzer = Depends(get_packet_analyzer)):
    if analyzer.is_running:
        analyzer.stop()
    return {"status": "Capture stopped"}


def check_root():
    print("Checking root privileges...")
    if os.geteuid() != 0:
        print("This script must be run as root!")
        args = ["sudo", sys.executable] + sys.argv
        os.execvp("sudo", args)


if __name__ == "__main__":
    check_root()
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
