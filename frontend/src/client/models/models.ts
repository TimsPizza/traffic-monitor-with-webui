export interface ICaptureFilter {
  src_ip?: string | null;
  dst_ip?: string | null;
  src_port?: number[];
  dst_port?: number[];
  protocol?: "tcp" | "udp" | "icmp" | "all";
}

export interface IAccessRecord {
  id: number;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  src_region: string;
  dst_port: number;
  protocol: string;
  timestamp: string;
}
