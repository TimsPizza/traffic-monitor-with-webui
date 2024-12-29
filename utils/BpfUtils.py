from typing import List, Optional
import re
from models.Filter import CaptureFilterRecord, Protocol, PortRangeInt
from pydantic import IPvAnyAddress


class BPFUtils:
    @staticmethod
    def build_filter_expression(records: List[CaptureFilterRecord]) -> str:
        if not records:
            return ""

        expressions = []
        for record in records:
            parts = []

            # Handle IP addresses
            if record.src_ip:
                parts.append(f"src host {record.src_ip}")
            if record.dst_ip:
                parts.append(f"dst host {record.dst_ip}")

            # Handle ports
            if record.src_port:
                parts.append(f"src port {record.src_port.port}")
            if record.dst_port:
                parts.append(f"dst port {record.dst_port.port}")

            # Handle protocol
            if record.protocol and record.protocol != Protocol.ALL:
                parts.append(record.protocol.value)

            if parts:
                expressions.append("(" + " and ".join(parts) + ")")

        return " or ".join(expressions)

    @staticmethod
    def parse_filter_expression(expression: str) -> List[CaptureFilterRecord]:
        if not expression.strip():
            return []

        # Split by OR operations
        or_parts = re.split(r"\)\s+or\s+\(", expression.strip("()"))
        records = []

        for part in or_parts:
            # Split by AND operations
            and_parts = part.split(" and ")
            record = CaptureFilterRecord()

            for condition in and_parts:
                condition = condition.strip()

                # Parse IP addresses
                if match := re.match(r"src\s+host\s+(\S+)", condition):
                    record.src_ip = IPvAnyAddress(match.group(1))
                elif match := re.match(r"dst\s+host\s+(\S+)", condition):
                    record.dst_ip = IPvAnyAddress(match.group(1))

                # Parse ports
                elif match := re.match(r"src\s+port\s+(\d+)", condition):
                    record.src_port = PortRangeInt(port=int(match.group(1)))
                elif match := re.match(r"dst\s+port\s+(\d+)", condition):
                    record.dst_port = PortRangeInt(port=int(match.group(1)))

                # Parse protocol
                elif condition in [p.value for p in Protocol]:
                    record.protocol = Protocol(condition)

            records.append(record)

        return records

    @staticmethod
    def validate_filter_expression(expression: str) -> bool:
        try:
            records = BPFUtils.parse_filter_expression(expression)
            rebuilt = BPFUtils.build_filter_expression(records)
            return bool(records) and bool(rebuilt)
        except Exception:
            return False
