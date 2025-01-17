import { IByTopSourceIps } from './request';
import { ITimeRange } from "./base";

export interface IByProtocolResponseItem extends IFullAccessRecordResponse {}
export interface IByProtocolResponse {
  records: IFullAccessRecordResponse[];
  total: number;
}

export interface IByRegionResponseItem extends IFullAccessRecordResponse {}
export interface IByRegionResponse {
  records: IFullAccessRecordResponse[];
  total: number;
}

export interface IByTimeRangeResponseItem extends IFullAccessRecordResponse {}
export interface IByTimeRangeResponse {
  records: IFullAccessRecordResponse[];
  total: number;
}

export interface IBySourceIpResponseItem extends IFullAccessRecordResponse{}
export interface IBySourceIPResponse {
  records: IFullAccessRecordResponse[];
  total: number;
}

export interface IByDestinationPortResponseItem extends IFullAccessRecordResponse {}
export interface IByDestinationPortResponse {
  records: IFullAccessRecordResponse[];
  total: number;
}

export interface IBySourceRegionResponseItem extends IFullAccessRecordResponse {}

export interface IBySourceRegionResponse {
  records: IFullAccessRecordResponse[];
  total: number;
}

export interface IByTopSourceIpsResponseItem  {
  ip: string;
  region: string;
  totalPackets: number;
  totalBytes: number;
}

export interface IByTopSourceIpsResponse {
  records: IByTopSourceIpsResponseItem[];
  total: number;
}

export interface ITrafficSummaryResponseItem {
  totalPackets: number;
  totalBytes: number;
  topSourceIps:IByTopSourceIpsResponse;
  protocolDistribution:IProtocolDistributionResponse;
  timeRange: ITimeRange;
}

export interface ITrafficSummaryResponse {
  total_packets: number;
  total_bytes: number;
}

export interface IProtocolDistributionResponseRecord {
  protocol: string;
  percentageCount: number;
  percentageBytes: number;
  packetCount: number;
  totalBytes: number;
}

export interface IProtocolDistributionResponse {
  distribution: IProtocolDistributionResponseRecord[];
  timeRange: ITimeRange;
}

export interface ITimeSeriesResponseItem {}

export interface ITimeSeriesResponse {
  records: IFullAccessRecordResponse[];
  total: number;
}

export interface IProtocolAnalysisResponseItem {}

export interface IProtocolAnalysisResponse {
  records: IFullAccessRecordResponse[];
  total: number;
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
