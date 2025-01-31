import { useInfiniteQuery, useQuery } from "react-query";
import { QueryService } from "../client/services/query";
import { useEffect, useState } from "react";
import { IPaginatedResponse } from "../client/api/models/response";
import { TQueryType } from "../client/types";
import useToast from "./useToast";

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
  const [maxPage, setMaxPage] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(0);
  const [hasNextPage, setHasNextPage] = useState<boolean>(false);
  const [hasPreviousPage, setHasPreviousPage] = useState<boolean>(false);
  // data will be <PaginatedResponse> regardlessly
  const [data, setData] = useState<TResponse | IPaginatedResponse<any>>();
  const [error, setError] = useState<any>();
  useEffect(() => {
    console.log("useAnalyticsQuery: queryType", queryType);
    console.log("useAnalyticsQuery: queryParams", queryParams);
  }, [queryParams, queryType]);
  const toast = useToast();
  const { isLoading } = useQuery({
    queryKey: ["analytics", queryType, queryParams],
    queryFn: async () => await mapping[queryType](queryParams),
    refetchInterval: refetchInterval || false, // dafault is false
    onError: (err) => {
      toast.error(err);
      setError(err);
    },
    onSuccess: (res) => {
      console.log("useAnalyticsQuery: success ", res.data.data);
      toast.success("Query Success");
      setData(res.data.data);
      setCurrentPage(res.data.page);
      setMaxPage(Math.ceil(res.data.total / res.data.page_size));
      setHasNextPage(res.data.page < maxPage);
      setHasPreviousPage(res.data.page > 1);
      console.log("maxPage", maxPage);
    },
  });
  return {
    data,
    currentPage,
    error,
    isLoading,
    hasNextPage,
    hasPreviousPage,
    maxPage,
  };
};
