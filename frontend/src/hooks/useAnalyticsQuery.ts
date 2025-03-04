import { useQuery } from "react-query";
import { ApiError } from "../client/api/models/base";
import {
  TQueryResponses
} from "../client/api/models/response";
import { QueryService } from "../client/services/query";
import { TQueryType } from "../client/types";
import useToast from "./useToast";

interface UseAnalyticsQueryOptions<T extends object> {
  queryType: TQueryType;
  params: T;
  refetchInterval?: number | false;
  enabled?: boolean;
  staleTime?: number;
  cacheTime?: number;
  retryDelay?: number;
  retry?: number;
}

export function useAnalyticsQuery<T extends object, R extends TQueryResponses>({
  queryType,
  params,
  refetchInterval = false,
  enabled = true,
  staleTime,
  cacheTime,
  retryDelay = 5000,
  retry = 3,
}: UseAnalyticsQueryOptions<T>) {
  const toast = useToast({
    position: "top-right",
  });
  console.log("useAnalyticsQuery:", queryType, params);
  const {
    data: queryResult,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<R, ApiError, R>({
    queryKey: ["analytics", queryType, params],
    queryFn: async () => {
      const response = await QueryService.query<T, R>(queryType, params);
      return response.data;
    },
    refetchInterval,
    retryDelay: retryDelay,
    retry: retry,

    onError: (error) => {
      toast.error("Query failed: " + error);
    },
    onSuccess: () => {
      toast.success("Success");
    },
    enabled,
    staleTime: staleTime ?? Infinity,
    cacheTime,
  });

  const hasNextPage = queryResult
    ? queryResult.page < Math.ceil(queryResult.total / queryResult.page_size)
    : false;
  const hasPreviousPage = queryResult ? queryResult.page > 1 : false;

  return {
    isError,
    isLoading,
    error,
    refetch,
    data: queryResult?.data,
    hasNextPage,
    hasPreviousPage,
    totalItems: queryResult?.total,
    currentPage: queryResult?.page,
    totalPages: queryResult
      ? Math.ceil(queryResult.total / queryResult.page_size)
      : 0,
  };
}
