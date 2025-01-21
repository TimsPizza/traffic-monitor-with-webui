import { useInfiniteQuery } from "react-query";
import { QueryService } from "../client/services/query";

export const useAnalyticsQuery = <T1 extends object, T2>(
  type: 'bySourceIP' | 'byProtocol' | 'byTimeRange' | 'byDestinationPort' | 'bySourceRegion' | 'protocolDistribution' | 'trafficSummary' | 'timeSeries' | 'protocolAnalysis' | 'topSourceIPs',
  payload: T1
) => {
  return useInfiniteQuery<T2>({
    queryKey: ["analytics", type, payload],
    queryFn: ({ pageParam = 1 }) => QueryService.query<T1 & { page: number }, T2>(type, {
      ...payload,
      page: pageParam
    }),
    getNextPageParam: (lastPage) => lastPage.hasNextPage ? lastPage.nextPage : undefined,
    getPreviousPageParam: (lastPage) => lastPage.hasPreviousPage ? lastPage.previousPage : undefined
  });
};
