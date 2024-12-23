import uvicorn
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from scapy.all import Ether, IP, TCP
import ipaddress
import os
import sys

from packet.PacketProducer import PacketProducer
from utils.DoubleBufferQueue import DoubleBufferQueue


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Starting")
    yield
    print("Exiting")


app = FastAPI(lifespan=life_span)
rules = [{"ip_range": ipaddress.IPv4Network("0.0.0.0/0")}]


@app.get("/")
async def read_root():
    return {"Hello": "World"}


def start_sniffing(filter_rule):
    double_buffer_queue = DoubleBufferQueue()
    producer = PacketProducer(double_buffer_queue, interface='eth0')
    double_buffer_queue.start()
    producer.start()


def packet_handler(pktlen, data, timestamp):
    if not data:
        return
    packet = Ether(data)
    # packet.show()
    if IP in packet:
        ip_layer = packet[IP]
        print(f"Source IP: {ip_layer.src}, Destination IP: {ip_layer.dst}")

    if TCP in packet:
        tcp_layer = packet[TCP]
        print(f"Source Port: {tcp_layer.sport}, Destination Port: {tcp_layer.dport}")


@app.get("/start_capture")
def start_capture(
    background_tasks: BackgroundTasks, src_ip: str = None, port: int = None
):
    filter_rule = ""
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
