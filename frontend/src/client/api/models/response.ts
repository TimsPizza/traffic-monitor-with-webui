import { ITimeRange } from "./base";

export interface IPaginatedResponse<T> {
  data: T;
  total: number;
  page: number;
  page_size: number;
}

export interface IFullAccessRecordResponse {
  id: string;
  region: string;
  src_ip: string;
  dst_port: number;
  protocol: string;
  timestamp: number;
  length: number;
}

export interface IByProtocolResponseItem extends IFullAccessRecordResponse {}
export interface IByProtocolResponse
  extends IPaginatedResponse<IByProtocolResponseItem> {}

export interface IByRegionResponseItem extends IFullAccessRecordResponse {}
export interface IByRegionResponse
  extends IPaginatedResponse<IByRegionResponseItem> {}

export interface IByTimeRangeResponseItem extends IFullAccessRecordResponse {}
export interface IByTimeRangeResponse
  extends IPaginatedResponse<IByTimeRangeResponseItem> {}

export interface IBySourceIpResponseItem extends IFullAccessRecordResponse {}
export interface IBySourceIPResponse
  extends IPaginatedResponse<IBySourceIpResponseItem> {}

export interface IByDestinationPortResponseItem
  extends IFullAccessRecordResponse {}
export interface IByDestinationPortResponse
  extends IPaginatedResponse<IByDestinationPortResponseItem> {}

export interface IBySourceRegionResponseItem
  extends IFullAccessRecordResponse {}
export interface IBySourceRegionResponse
  extends IPaginatedResponse<IBySourceRegionResponseItem> {}

export interface IByTopSourceIpsResponseItem {
  ip: string;
  region: string;
  totalPackets: number;
  totalBytes: number;
}
export interface IByTopSourceIpsResponse
  extends IPaginatedResponse<IByTopSourceIpsResponseItem> {}

export interface ITrafficSummaryResponseItem {
  total_packets: number;
  total_bytes: number;
  top_source_ips: IByTopSourceIpsResponse;
  protocol_distribution: IProtocolDistributionResponse;
  time_range: ITimeRange;
}
export interface ITrafficSummaryResponse
  extends IPaginatedResponse<ITrafficSummaryResponseItem> {}

export interface IProtocolDistributionResponseRecord {
  distribution: Array<{
    protocol: string;
    percentage_count: number;
    percentage_bytes: number;
    packet_count: number;
    total_bytes: number;
  }>;
  time_range: ITimeRange;
}
export interface IProtocolDistributionResponse
  extends IPaginatedResponse<IProtocolDistributionResponseRecord> {}

export type ITimeSeriesResponseItem = Array<{
  total_packets: number;
  total_bytes: number;
  time_range: ITimeRange;
}>;
export interface ITimeSeriesResponse
  extends IPaginatedResponse<ITimeSeriesResponseItem> {}

export type TSignUpResponse = {
  username: string;
  password_hash: string;
  created_at: number;
  last_login: number;
  is_active: boolean;
};

export type TAuthResponse = {
  access_token: string;
  token_type: string;
};

// 配置相关响应类型 (Configuration related response types)
export type TFilterAllResponse = Array<{
  src_ip?: string | null;
  dst_ip?: string | null;
  src_port?: number[] | null;
  dst_port?: number[] | null;
  protocol?: "tcp" | "udp" | "icmp" | "all" | null;
  operation: "Include" | "Exclude";
  direction: "Inbound" | "Outbound";
}>;

export interface IProtocolPortMappingResponse {
  rules: Array<{
    protocol: string;
    ports: number[]; // 修改为直接的端口数组
  }>;
}

export interface INetworkInterfacesResponse {
  interfaces: string[];
  selected: string;
}
