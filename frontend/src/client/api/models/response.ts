import { ITimeRange } from "./base";

export interface IPaginatedResponse<T> {
  data: T[];
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
export interface IByProtocolResponse extends IPaginatedResponse<IByProtocolResponseItem> {}

export interface IByRegionResponseItem extends IFullAccessRecordResponse {}
export interface IByRegionResponse extends IPaginatedResponse<IByRegionResponseItem> {}

export interface IByTimeRangeResponseItem extends IFullAccessRecordResponse {}
export interface IByTimeRangeResponse extends IPaginatedResponse<IByTimeRangeResponseItem> {}

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
  protocol: string;
  percentage_count: number;
  percentage_bytes: number;
  packet_count: number;
  total_bytes: number;
}
export interface IProtocolDistributionResponse
  extends IPaginatedResponse<IProtocolDistributionResponseRecord> {}

export interface ITimeSeriesResponseItem {}
export interface ITimeSeriesResponse
  extends IPaginatedResponse<ITimeSeriesResponseItem> {}

export interface IProtocolAnalysisResponseItem {}
export interface IProtocolAnalysisResponse
  extends IPaginatedResponse<IProtocolAnalysisResponseItem> {}

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
