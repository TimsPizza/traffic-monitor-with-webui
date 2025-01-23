import { useInfiniteQuery, useQuery } from "react-query";
import { QueryService } from "../client/services/query";
import { useState } from "react";
import { IPaginatedResponse } from "../client/api/models/response";

type TQueryType =
  | "bySourceIP"
  | "byProtocol"
  | "byTimeRange"
  | "byDestinationPort"
  | "bySourceRegion"
  | "protocolDistribution"
  | "trafficSummary"
  | "timeSeries"
  | "protocolAnalysis"
  | "topSourceIPs";

const mapping: Record<
  TQueryType,
  (params: any) => Promise<IPaginatedResponse<any>>
> = {
  bySourceIP: QueryService.queryBySourceIP,
  byProtocol: QueryService.queryByProtocol,
  byTimeRange: QueryService.queryByTimeRange,
  byDestinationPort: QueryService.queryByDestinationPort,
  bySourceRegion: QueryService.queryBySourceRegion,
  protocolDistribution: QueryService.queryProtocolDistribution,
  trafficSummary: QueryService.queryTrafficSummary,
  timeSeries: QueryService.queryTimeSeries,
  protocolAnalysis: QueryService.queryProtocolAnaysis,
  topSourceIPs: QueryService.queryTopSourceIPs,
};

export const useAnalyticsQuery = <TRequest = any, TResponse = any>(
  queryType: TQueryType,
  queryParams: TRequest,
  refetchInterval: number | false = false,
) => {
  const [hasPreviousPage, setHasPreviousPage] = useState(false);
  const [hasNextPage, setHasNextPage] = useState(false);
  // data will be paginated response regardlessly
  const [data, setData] = useState<TResponse | IPaginatedResponse<any>>();
  const [error, setError] = useState<any>();
  const { isLoading } = useQuery({
    queryKey: ["analytics", queryType, queryParams],
    queryFn: async () => await mapping[queryType](queryParams),
    refetchInterval: refetchInterval || false, // dafault is false
    onError: (err) => {
      setError(err);
    },
    onSuccess: (res) => {
      setData(res);
      setHasNextPage(res.page * res.page_size < res.total);
      setHasPreviousPage(res.page > 1);
      res;
    },
  });
  return {
    data,
    error,
    isLoading,
    hasPreviousPage,
    hasNextPage,
  };
};
