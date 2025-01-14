import { useInfiniteQuery } from 'react-query';
import { QueryService } from '../client/services/services';
import { TQueryParams, TQueryType } from '../client/types';
import { useEffect } from 'react';

export const useAnalyticsQuery = (
  queryType: TQueryType,
  initialParams: TQueryParams
) => {
  useEffect(() => {
    console.log('useAnalyticsQuery mounted');
  
    return () => {
      
    }
  }, [])
  
  const {
    data,
    isLoading,
    isError,
    fetchNextPage,
    fetchPreviousPage,
    hasPreviousPage,
    hasNextPage,
    isFetchingNextPage,
    error
  } = useInfiniteQuery(
    ['analytics', queryType, initialParams],
    ({ pageParam = 1 }) => 
      QueryService.queryPackets(queryType, {
        ...initialParams,
        page: pageParam,
        pageSize: initialParams.pageSize || 50
      }),
    {
      getNextPageParam: (lastPage, allPages) => {
        const totalItems = lastPage.totalCount || 0;
        const fetchedItems = allPages.reduce((sum, page) => sum + page.items.length, 0);
        return fetchedItems < totalItems ? allPages.length + 1 : undefined;
      },
      staleTime: 1000 * 60 * 5 // 5 minutes
    }
  );

  return {
    data: data?.pages.flatMap(page => page.items) || [],
    isLoading,
    isError,
    error,
    fetchNextPage,
    fetchPreviousPage,
  hasPreviousPage,  
    hasNextPage,
    isFetchingNextPage
  };
};
