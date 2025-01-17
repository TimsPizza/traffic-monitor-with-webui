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
  sourceIP: string;
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

export interface ICaptureFilterSetting {
  src_ip?: string | null;
  dst_ip?: string | null;
  src_port?: number[];
  dst_port?: number[];
  protocol?: "tcp" | "udp" | "icmp" | "all";
}
