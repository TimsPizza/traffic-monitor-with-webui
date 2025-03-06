import { IPagination, IRegion, ITimeRange } from "./base";

export interface IBySourceRegion extends IRegion, IPagination, ITimeRange {}

export interface IByTimeRange extends IPagination, ITimeRange {}

export interface IByProtocol extends IPagination, ITimeRange {
  protocol: string;
}

export interface IByTopSourceIps extends IPagination, ITimeRange {}

export interface IByDestinationPort extends IPagination, ITimeRange {
  port: number;
}

export interface IBySourceIP extends IPagination, ITimeRange {
  ip_address: string;
}

export interface IProtocolDistribution extends ITimeRange, IPagination {}

export interface ITrafficSummary extends ITimeRange, IPagination {}

export interface ITimeSeries extends ITimeRange, IPagination {}

export interface IProtocolAnalysis extends ITimeRange, IPagination {}

export type TLoginForm = {
  username: string;
  password: string;
};

export type TUser = {
  username: string;
};

export type TSignUpForm = {
  username: string;
  password: string;
};

// 配置相关请求类型 (Configuration related request types)

export interface IPortRange {
  port: number;  // 1-65535
}

export interface IProtocolPortMappingRule {
  protocol: string;
  port: IPortRange;  // 修复：使用单个 IPortRange 而不是数组
}

export interface ICaptureFilter {
  src_ip?: string | null;
  dst_ip?: string | null;
  src_port?: number[] | null;
  dst_port?: number[] | null;
  protocol?: 'tcp' | 'udp' | 'icmp' | 'all' | null;
  operation: 'Include' | 'Exclude';
  direction: 'Inbound' | 'Outbound';
}
