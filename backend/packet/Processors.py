import datetime
from uuid import uuid4
import yaml
import os
from .Packet import Layer, ProcessedPacket
from service.GeoIpService import GeoIPSingleton
import struct
from scapy.all import TCP, Raw
import logging

logger = logging.getLogger(__name__)

# 读取配置文件获取端口-协议映射 (Read config file to get port-protocol mappings)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")


def _load_port_protocol_map() -> dict:
    """从配置文件加载端口-协议映射 (Load port-protocol mappings from config file)"""
    try:
        if not os.path.exists(CONFIG_PATH):
            return {}
        with open(CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f) or {}
            return {
                rule["port"]["port"]: rule["protocol"]
                for rule in config.get("rules", [])
            }
    except Exception as e:
        logger.error(f"Error loading port-protocol mappings: {e}")
        return {}


def check_udp(scapy_packet, packet: ProcessedPacket) -> None:
    if scapy_packet.haslayer("UDP"):
        packet.src_port = scapy_packet["UDP"].sport
        packet.dst_port = scapy_packet["UDP"].dport
        packet.protocol = "UDP"
        packet.source_ip = scapy_packet["IP"].src
        packet.layer = Layer.TRANSPORT


def check_tcp(scapy_packet, packet: ProcessedPacket) -> None:
    if scapy_packet.haslayer("TCP"):
        packet.src_port = scapy_packet["TCP"].sport
        packet.dst_port = scapy_packet["TCP"].dport
        packet.source_ip = scapy_packet["IP"].src
        packet.protocol = Layer.TRANSPORT


def check_http(payload: bytes) -> bool:
    """HTTP协议特征检测"""
    if len(payload) < 4:
        return False
    try:
        decoded = payload.decode("utf-8", "ignore").strip()
        return decoded.startswith(
            (
                "GET ",
                "POST ",
                "PUT ",
                "DELETE ",
                "HEAD ",
                "OPTIONS ",
                "HTTP/1.0",
                "HTTP/1.1",
            )
        ) or any(s in decoded for s in ("Host: ", "User-Agent: ", "Content-Type: "))
    except UnicodeDecodeError:
        return False


def check_tls(payload: bytes) -> bool:
    """TLS/SSL协议特征检测"""
    if len(payload) >= 3:
        content_type = payload[0]
        # TLS handshake content type is 0x16
        if content_type == 0x16:
            # Check for Handshake protocol (0x01)
            if len(payload) >= 6 and payload[5] == 0x01:
                return True
    return False


def check_ssh(payload: bytes) -> bool:
    """SSH协议特征检测"""
    return len(payload) >= 4 and payload.startswith(b"SSH")


def check_dns_tcp(payload: bytes) -> bool:
    """DNS over TCP特征检测"""
    if len(payload) < 2:
        return False
    dns_length = struct.unpack("!H", payload[:2])[0]
    return len(payload) >= dns_length + 2 and dns_length > 0


def check_ftp(payload: bytes) -> bool:
    """FTP协议特征检测"""
    try:
        decoded = payload.decode("ascii", "ignore").strip()
        return (
            decoded.startswith(("USER ", "PASS ", "CWD ", "LIST"))
            or decoded[:3].isdecimal()
            and len(decoded) >= 4
            and decoded[3] == " "
        )
    except UnicodeDecodeError:
        return False


def check_smtp(payload: bytes) -> bool:
    """SMTP协议特征检测"""
    try:
        decoded = payload.decode("ascii", "ignore").strip()
        return (
            decoded.startswith(("EHLO ", "HELO ", "MAIL FROM:")) or decoded[:3] == "220"
        )
    except UnicodeDecodeError:
        return False


def check_rtsp(payload: bytes) -> bool:
    """RTSP协议特征检测"""
    try:
        decoded = payload.decode("ascii", "ignore").strip()
        return (
            decoded.startswith(("OPTIONS ", "DESCRIBE ", "SETUP "))
            or "RTSP/1.0" in decoded
        )
    except UnicodeDecodeError:
        return False


def check_smb(payload: bytes) -> bool:
    """SMB协议特征检测"""
    return len(payload) >= 4 and payload[0] == 0x00 and payload[1:4] == b"SMB"


def check_ntp(payload: bytes) -> bool:
    """NTP协议特征检测"""
    return len(payload) >= 1 and (payload[0] & 0b11000111) == 0b00000011


def check_rtp(payload: bytes) -> bool:
    """RTP协议特征检测"""
    return len(payload) >= 12 and (payload[0] & 0xC0) == 0x80


def check_quic(payload: bytes) -> bool:
    """QUIC协议特征检测"""
    return len(payload) >= 6 and (payload[0] & 0x80) == 0x80 and payload[4:6] == b"Q0"


def check_bittorrent(payload: bytes) -> bool:
    """BitTorrent协议特征检测"""
    return payload.startswith(b"BitTorrent protocol") or b"8:announce" in payload


def check_rdp(payload: bytes) -> bool:
    """RDP协议特征检测"""
    return len(payload) >= 4 and payload[0] == 0x03 and payload[1] == 0x00


def check_sip(payload: bytes) -> bool:
    """SIP协议特征检测"""
    try:
        decoded = payload.decode("ascii", "ignore").strip()
        return decoded.startswith(("INVITE ", "REGISTER ", "SIP/2.0 "))
    except UnicodeDecodeError:
        return False


def check_mysql(payload: bytes) -> bool:
    """MySQL协议特征检测"""
    if len(payload) < 4:
        return False
    length = struct.unpack("<I", payload[:3] + b"")[0]
    return len(payload) >= length + 4 and payload[3] == 0x00


def check_application_protocol(scapy_packet, packet: ProcessedPacket) -> None:
    if not scapy_packet.haslayer(TCP):
        return

    packet.layer = Layer.APPLICATION
    sport = scapy_packet[TCP].sport
    dport = scapy_packet[TCP].dport
    payload = bytes(scapy_packet[TCP].payload) if scapy_packet.haslayer(Raw) else b""

    # 按最常见协议排序的特征检测 (Payload-based protocol detection sorted by most common protocols)
    protocol_checks = [
        (check_http, "HTTP"),
        (check_tls, "HTTPS"),
        (check_ssh, "SSH"),
        (check_dns_tcp, "DNS"),
        (check_ftp, "FTP"),
        (check_smtp, "SMTP"),
        (check_rtsp, "RTSP"),
        (check_smb, "SMB"),
        (check_ntp, "NTP"),
        (check_rdp, "RDP"),
        (check_quic, "QUIC"),
        (check_sip, "SIP"),
        (check_mysql, "MySQL"),
        (check_bittorrent, "BitTorrent"),
        (check_rtp, "RTP"),
    ]

    # 先通过载荷检测 (First check by payload)
    for check_func, proto in protocol_checks:
        if check_func(payload):
            packet.protocol = proto
            return

    # 从配置文件加载端口映射 (Load port mappings from config)
    port_map = _load_port_protocol_map()
    packet.protocol = port_map.get(sport) or port_map.get(dport) or "Unknown"


def check_ssh_type(scapy_packet, packet: ProcessedPacket):
    if not (
        scapy_packet.haslayer("TCP")
        and (scapy_packet["TCP"].sport == 22 or scapy_packet["TCP"].dport == 22)
    ):
        return
    payload = bytes(scapy_packet["TCP"].payload)

    if len(payload) < 6:  # SSH packets are at least 6 bytes
        return

    msg_type = payload[5] if len(payload) > 5 else 0

    if msg_type in (20, 21):  # SSH_MSG_KEXINIT
        packet.protocol = "SSH-HANDSHAKE"
    elif msg_type == 50:  # SSH_MSG_USERAUTH_REQUEST
        packet.protocol = "SSH-AUTH"
    elif msg_type >= 90:  # Channel related messages
        packet.protocol = "SSH-DATA"


def check_src_ip_region(scapy_packet, packet: ProcessedPacket):
    if not scapy_packet.haslayer("IP") or GeoIPSingleton.given_up:
        return
    if packet.source_ip != "":
        src_ip = packet.source_ip
    else:
        src_ip = scapy_packet["IP"].src

    region = GeoIPSingleton.check_region(src_ip)
    packet.src_region = region if region else "Unknown"


def check_handshake(scapy_packet, packet: ProcessedPacket) -> None:
    if not scapy_packet.haslayer("TCP"):
        return

    tcp = scapy_packet["TCP"]
    # Check for SYN flag without ACK (initial handshake)
    if tcp.flags & 0x02 and not tcp.flags & 0x10:
        packet.is_handshake = True


def add_uuid(scapy_packet, packet: ProcessedPacket) -> None:
    packet._id = str(uuid4())
