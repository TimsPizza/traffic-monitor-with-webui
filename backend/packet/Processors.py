from .Packet import Layer, ProcessedPacket


def check_udp(scapy_packet, packet: ProcessedPacket) -> None:
    if scapy_packet.haslayer("UDP"):
        packet.src_port = scapy_packet["UDP"].sport
        packet.dst_port = scapy_packet["UDP"].dport
        packet.protocol += "UDP"
        packet.layer = Layer.TRANSPORT


def check_tcp(scapy_packet, packet: ProcessedPacket) -> None:
    if scapy_packet.haslayer("TCP"):
        packet.src_port = scapy_packet["TCP"].sport
        packet.dst_port = scapy_packet["TCP"].dport
        packet.protocol = Layer.TRANSPORT


def check_application_protocol(scapy_packet, packet: ProcessedPacket) -> None:
    if not scapy_packet.haslayer("TCP"):
        return
    packet.layer = Layer.APPLICATION

    sport = scapy_packet["TCP"].sport
    dport = scapy_packet["TCP"].dport

    match (sport, dport):
        case (80, _) | (_, 80):
            packet.protocol = "HTTP"
        case (443, _) | (_, 443):
            packet.protocol = "HTTPS"
        case (53, _) | (_, 53):
            packet.protocol = "DNS"
        case (21, _) | (_, 21):
            packet.protocol = "FTP"
        case (22, _) | (_, 22):
            packet.protocol = "SSH"
        case (23, _) | (_, 23):
            packet.protocol = "Telnet"
        case (25, _) | (_, 25):
            packet.protocol = "SMTP"
        case (110, _) | (_, 110):
            packet.protocol = "POP3"
        case (143, _) | (_, 143):
            packet.protocol = "IMAP"
        case (3306, _) | (_, 3306):
            packet.protocol = "MySQL"
        case (3389, _) | (_, 3389):
            packet.protocol = "RDP"
        case (5900, _) | (_, 5900):
            packet.protocol = "VNC"
        case (6379, _) | (_, 6379):
            packet.protocol = "Redis"
        case (27017, _) | (_, 27017):
            packet.protocol = "MongoDB"
        case (5432, _) | (_, 5432):
            packet.protocol = "PostgreSQL"
        case (8080, _) | (_, 8080):
            packet.protocol = "HTTP-ALT"
        case (8443, _) | (_, 8443):
            packet.protocol = "HTTPS-ALT"
        case (161, _) | (_, 161):
            packet.protocol = "SNMP"
        case (389, _) | (_, 389):
            packet.protocol = "LDAP"
        case (636, _) | (_, 636):
            packet.protocol = "LDAPS"
        case (5060, _) | (_, 5060):
            packet.protocol = "SIP"
        case (5061, _) | (_, 5061):
            packet.protocol = "SIPS"
        case (1194, _) | (_, 1194):
            packet.protocol = "OpenVPN"
        case (1723, _) | (_, 1723):
            packet.protocol = "PPTP"
        case (5000, _) | (_, 5000):
            packet.protocol = "UPnP"
        case (5353, _) | (_, 5353):
            packet.protocol = "mDNS"
        case (1900, _) | (_, 1900):
            packet.protocol = "SSDP"
        case (514, _) | (_, 514):
            packet.protocol = "Syslog"
        case (69, _) | (_, 69):
            packet.protocol = "TFTP"
        case (123, _) | (_, 123):
            packet.protocol = "NTP"
        case (67, _) | (_, 67) | (68, _) | (_, 68):
            packet.protocol = "DHCP"
        case (137, _) | (_, 137) | (138, _) | (_, 138) | (139, _) | (_, 139):
            packet.protocol = "NetBIOS"
        case (445, _) | (_, 445):
            packet.protocol = "SMB"
        case (520, _) | (_, 520):
            packet.protocol = "RIP"
        case (179, _) | (_, 179):
            packet.protocol = "BGP"
        case (88, _) | (_, 88):
            packet.protocol = "Kerberos"
        case (548, _) | (_, 548):
            packet.protocol = "AFP"
        case (631, _) | (_, 631):
            packet.protocol = "IPP"
        case (873, _) | (_, 873):
            packet.protocol = "Rsync"
        case (992, _) | (_, 992):
            packet.protocol = "Telnet over SSL"
        case (993, _) | (_, 993):
            packet.protocol = "IMAPS"
        case (995, _) | (_, 995):
            packet.protocol = "POP3S"
        case (1812, _) | (_, 1812) | (1813, _) | (_, 1813):
            packet.protocol = "RADIUS"
        case (1645, _) | (_, 1645) | (1646, _) | (_, 1646):
            packet.protocol = "RADIUS (legacy)"
        case (3478, _) | (_, 3478) | (3479, _) | (_, 3479):
            packet.protocol = "STUN/TURN"
        case (500, _) | (_, 500) | (4500, _) | (_, 4500):
            packet.protocol = "IPSec"
        case (119, _) | (_, 119):
            packet.protocol = "NNTP"
        case (563, _) | (_, 563):
            packet.protocol = "NNTPS"
        case (6667, _) | (_, 6667):
            packet.protocol = "IRC"
        case (6697, _) | (_, 6697):
            packet.protocol = "IRC over SSL"
        case (10000, _) | (_, 10000):
            packet.protocol = "Webmin"
        case (11211, _) | (_, 11211):
            packet.protocol = "Memcached"
        case (27015, _) | (_, 27015):
            packet.protocol = "Steam"
        case (25565, _) | (_, 25565):
            packet.protocol = "Minecraft"
        case _:
            packet.protocol = "Unknown"


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
        packet.protocol += "-Handshake"
    elif msg_type == 50:  # SSH_MSG_USERAUTH_REQUEST
        packet.protocol += "-Auth"
    elif msg_type >= 90:  # Channel related messages
        packet.protocol += "-Data"
        
def check_src_ip_region(scapy_packet, packet: ProcessedPacket):
    from core.services import GeoIPSingleton 
    if not scapy_packet.haslayer("IP") or GeoIPSingleton.given_up:
        return
    ip = scapy_packet["IP"]
    src_ip = ip.src
    region = GeoIPSingleton.check_region(src_ip)
    packet.src_region = region if region else "Unknown"

