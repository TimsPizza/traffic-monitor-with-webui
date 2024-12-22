from multiprocessing import Pool, Queue
from typing import List, Dict
from scapy.all import Ether, IP, TCP


class PacketFilter:
    def __init__(self, allowed_ports: List[int] = None, ip_ranges: List[str] = None):
        self.allowed_ports = set(allowed_ports) if allowed_ports else None
        self.ip_ranges = ip_ranges
        self.packet_queue = Queue(maxsize=1000)
        self.pool = Pool(processes=4)
        
    def filter_packet(self, packet_data: Dict):
        """Early filter before detailed processing"""
        if TCP in packet_data['packet']:
            tcp_layer = packet_data['packet'][TCP]
            if self.allowed_ports and tcp_layer.dport not in self.allowed_ports:
                return False
        return True

    def process_packet_batch(self, packets: List[Dict]):
        """Process packets in batch"""
        filtered_packets = []
        for packet_data in packets:
            if self.filter_packet(packet_data):
                filtered_packets.append(packet_data)
        return filtered_packets
