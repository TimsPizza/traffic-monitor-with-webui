import { useCallback, useEffect, useMemo } from "react";
import { useAnalyticsQuery } from "./useAnalyticsQuery";
import {
  ProtocolCardData,
  ProtocolCardQueryParams,
} from "../types/hooks/types";
import { bytesToSize } from "../utils/tools";
import { IProtocolDistributionResponseRecord } from "../client/api/models/response";

export const useCardData = ({
  timeRange,
  queryType,
  compareWithPrevious = false,
  protocol,
}: ProtocolCardQueryParams): ProtocolCardData => {
  // 当前时间段的查询
  const currentQuery = useAnalyticsQuery({
    queryType: queryType as any,
    params: {
      start: timeRange.start,
      end: timeRange.end,
      page: 1,
      page_size: 10,
    },
  });

  // 前一时间段的查询（如果需要比较）
  const previousQuery = useAnalyticsQuery({
    queryType: queryType,
    params: {
      start: timeRange.start - (timeRange.end - timeRange.start),
      end: timeRange.start,
      page: 1,
      page_size: 10,
    },
    enabled: compareWithPrevious,
  });

  // 计算趋势
  const calculateTrend = useCallback(
    (current?: number, previous?: number): number | undefined => {
      if (current === undefined || previous === undefined || previous === 0) {
        return undefined;
      }
      return ((current - previous) / previous) * 100;
    },
    [],
  );

  // 处理数据
  const processedData = useMemo(() => {
    const defaultData: ProtocolCardData = {
      current: {
        value: 0,
        label: "0",
        secondaryValue: 0,
      },
      isLoading:
        currentQuery.isLoading ||
        (compareWithPrevious && previousQuery.isLoading),
      error: currentQuery.error || previousQuery.error || null,
    };

    if (!currentQuery.data) {
      return defaultData;
    }

    // 根据不同的metric处理数据
    const current = currentQuery.data as IProtocolDistributionResponseRecord;
    const previous = previousQuery.data as IProtocolDistributionResponseRecord;
    // 处理复杂对象类型的数据
    const currentTarget = current.distribution.find(
      (predicate) => predicate.protocol === protocol,
    );
    const previousTarget = previous?.distribution.find(
      (predicate) => predicate.protocol === protocol,
    );

    if (currentTarget) {
      const value = currentTarget.total_bytes;
      const result = bytesToSize(value);
      defaultData.current = {
        value: parseFloat(result.size),
        label: result.unit,
        secondaryValue: currentTarget.packet_count,
      };
    }
    if (compareWithPrevious && previousTarget) {
      const value = previousTarget.total_bytes;
      const result = bytesToSize(value);
      defaultData.trend = calculateTrend(
        defaultData.current.value,
        parseFloat(result.size),
      );
    }
    return defaultData;
  }, [
    currentQuery.data,
    previousQuery.data,
    currentQuery.isLoading,
    previousQuery.isLoading,
    currentQuery.error,
    previousQuery.error,
    compareWithPrevious,
    calculateTrend,
    protocol,
  ]);

  useEffect(() => {
    console.log("useCardData returning:", processedData);
  }, [processedData]);

  return processedData;
};
