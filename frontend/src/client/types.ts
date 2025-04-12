export type TQueryType =
  | "bySourceIP"
  | "byProtocol"
  | "byTimeRange"
  | "byDestinationPort"
  | "bySourceRegion"
  | "protocolDistribution"
  | "trafficSummary"
  | "timeSeries"
  | "topSourceIPs";

export type TQueryParams = {
  start?: number;
  end?: number;
  protocol?: string;
  ip_address?: string;
  page?: number;
  page_size?: number;
  port?: number;
  region?: string;
};

export interface IPageInfo {
  currentPage: number;
  pageSize: number;
  total: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}
