import { useQuery } from "react-query";
import { QueryService } from "../client/services/query";
import { TQueryType } from "../client/types";
import useToast from "./useToast";
import { IPaginatedResponse } from "../client/api/models/response";

interface UseAnalyticsQueryOptions<T extends object> {
  queryType: TQueryType;
  params: T;
  refetchInterval?: number | false;
  enabled?: boolean;
  staleTime?: number;
  cacheTime?: number;
}

export function useAnalyticsQuery<T extends object, R>({
  queryType,
  params,
  refetchInterval = false,
  enabled = true,
  staleTime,
  cacheTime,
}: UseAnalyticsQueryOptions<T>) {
  const toast = useToast();

  const {
    data: queryResult,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<IPaginatedResponse<R>, unknown, IPaginatedResponse<R>>({
    queryKey: ["analytics", queryType, params],
    queryFn: async (): Promise<IPaginatedResponse<R>> => {
      const response = await QueryService.query<T, IPaginatedResponse<R>>(
        queryType,
        params,
      );
      return {
        data: response.data.data || [],
        total: response.data.total || 0,
        page: response.data.page || 1,
        page_size: response.data.page_size || 10,
      };
    },
    refetchInterval,
    onError: (error) => {
      toast.error("Query failed: " + error);
    },
    onSuccess: () => {
      toast.success("Query success");
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
