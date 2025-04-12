import { useMemo } from "react";
import { useAnalyticsQuery } from "./useAnalyticsQuery";
import { ChartData, ChartQueryParams } from "../types/hooks/types";
import { bytesToSize } from "../utils/tools";
import { unix2DateString } from "../utils/timetools";

export const useChartData = ({
  timeRange,
  queryType: metric,
  chartType,
  interval = 3600, // 默认1小时间隔
}: ChartQueryParams): ChartData => {
  // 查询设置
  const queryParams = useMemo(() => {
    return {
      queryType: metric,
      params: {
        start: timeRange.start ?? Date.now() / 1e3 - 86400 * 7,
        end: timeRange.end ?? Date.now() / 1e3,
        interval: interval,
        page: 1,
        page_size: 100,
      },
    };
  }, [timeRange, metric, chartType, interval]);

  // 执行查询
  const query = useAnalyticsQuery(queryParams);

  // 处理数据
  const processedData = useMemo(() => {
    const defaultData: ChartData = {
      data: [],
      isLoading: query.isLoading,
      error: query.error as Error | undefined,
    };

    if (!query.data) {
      return defaultData;
    }

    if (chartType === "trend") {
      // 处理时间序列数据
      if (!Array.isArray(query.data) || query.data.length === 0) {
        return defaultData;
      }

      return {
        ...defaultData,
        data: query.data
          .map((item) => {
            const bytes = bytesToSize(item.total_bytes);
            return {
              name: unix2DateString(item.time_range.start),
              value: parseFloat(bytes.size.toString()),
              timestamp: item.time_range.start,
            };
          })
          .sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0)),
      };
    }

    // 处理分布数据
    if (chartType === "distribution") {
      const data = query.data.distribution.map((item) => ({
        name: item.protocol || "Unknown",
        value: item.percentage_bytes || 0,
        // @ts-ignore
        timestamp: item.time_range.end,
      }));
      return {
        ...defaultData,
        // @ts-ignore
        data: data,
      };
    }

    return defaultData;
  }, [query.data, query.isLoading, query.error, chartType]);
  return processedData;
};
