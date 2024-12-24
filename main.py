import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.logger import logger
from contextlib import asynccontextmanager
from scapy.all import Ether, IP, TCP
import os
import sys

from packet.PacketConsumer import PacketConsumer
from packet.Packet import CapturedPacket
from packet.PacketProducer import PacketProducer
from utils.DoubleBufferQueue import DoubleBufferQueue


@asynccontextmanager
async def life_span(app: FastAPI):
    logger.info("Starting")
    yield
    logger.info("Stopping")


app = FastAPI(lifespan=life_span)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


def start_sniffing(filter_rule):
    double_buffer_queue = DoubleBufferQueue[CapturedPacket]()
    producer = PacketProducer(double_buffer_queue, interface="eth0", filter=None)
    consumer = PacketConsumer(double_buffer_queue, max_workers=8, batch_size=128)
    double_buffer_queue.start()
    producer.start()
    consumer.start()


@app.get("/start_capture")
def start_capture(
    background_tasks: BackgroundTasks, src_ip: str = None, port: int = None
):
    filter_rule = "tcp and (dst port 22 or dst port 23 or dst port 80 or dst port 443 or dst port 8080 or dst port 9000 or dst port 1026)"
    if src_ip:
        filter_rule += f"src host {src_ip} "
    if port:
        if filter_rule:
            filter_rule += "and "
        filter_rule += f"port {port}"

    if not filter_rule:
        filter_rule = "tcp"  # 默认过滤所有 TCP 包

    background_tasks.add_task(start_sniffing, filter_rule)
    return {"status": "Capturing started with filter:", "filter": filter_rule}


# Add at the start of your main.py


def check_root():
    print("Checking root privileges...")
    if os.geteuid() != 0:
        print("This script must be run as root!")
        args = ["sudo", sys.executable] + sys.argv
        os.execvp("sudo", args)


if __name__ == "__main__":
    check_root()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
