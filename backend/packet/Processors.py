import datetime
from uuid import uuid4

from .Packet import Layer, ProcessedPacket
from service.GeoIpService import GeoIPSingleton
import struct
from scapy.all import TCP, Raw


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
    return len(payload) >= 4 and payload[0] == 0x00 and payload[1:4] == b"\xffSMB"


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
    return payload.startswith(b"\x13BitTorrent protocol") or b"8:announce" in payload


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
    length = struct.unpack("<I", payload[:3] + b"\x00")[0]
    return len(payload) >= length + 4 and payload[3] == 0x00


def check_application_protocol(scapy_packet, packet: ProcessedPacket) -> None:
    if not scapy_packet.haslayer(TCP):
        return

    packet.layer = Layer.APPLICATION
    sport = scapy_packet[TCP].sport
    dport = scapy_packet[TCP].dport
    payload = bytes(scapy_packet[TCP].payload) if scapy_packet.haslayer(Raw) else b""

    # sort by most common protocols
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

    # first check by payload
    for check_func, proto in protocol_checks:
        if check_func(payload):
            packet.protocol = proto
            return

    # fallback to port-based protocol detection
    port_map = {
        80: "HTTP",
        443: "HTTPS",
        53: "DNS",
        21: "FTP",
        22: "SSH",
        25: "SMTP",
        110: "POP3",
        143: "IMAP",
        3306: "MySQL",
        3389: "RDP",
        5900: "VNC",
        6379: "Redis",
        27017: "MongoDB",
        5432: "PostgreSQL",
        8080: "HTTP-ALT",
        8443: "HTTPS-ALT",
        161: "SNMP",
        389: "LDAP",
        636: "LDAPS",
        5060: "SIP",
        5061: "SIPS",
        1194: "OpenVPN",
        1723: "PPTP",
        5000: "UPnP",
        5353: "mDNS",
        1900: "SSDP",
        514: "Syslog",
        69: "TFTP",
        123: "NTP",
        67: "DHCP",
        68: "DHCP",
        137: "NetBIOS",
        138: "NetBIOS",
        139: "NetBIOS",
        445: "SMB",
        520: "RIP",
        179: "BGP",
        88: "Kerberos",
        548: "AFP",
        631: "IPP",
        873: "Rsync",
        992: "Telnet over SSL",
        993: "IMAPS",
        995: "POP3S",
        1812: "RADIUS",
        1813: "RADIUS",
        1645: "RADIUS (legacy)",
        1646: "RADIUS (legacy)",
        3478: "STUN/TURN",
        3479: "STUN/TURN",
        500: "IPSec",
        4500: "IPSec",
        119: "NNTP",
        563: "NNTPS",
        6667: "IRC",
        6697: "IRC over SSL",
        10000: "Webmin",
        11211: "Memcached",
        27015: "Steam",
        25565: "Minecraft",
    }

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
