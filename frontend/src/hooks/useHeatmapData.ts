import { useMemo } from "react";
import {
  IByTopSourceIpsResponseItem,
  IProtocolDistributionResponseRecord,
  IPaginatedResponse,
} from "../client/api/models/response";
import { HeatmapData, HeatmapQueryParams } from "../types/hooks/types";
import { bytesToSize } from "../utils/tools";
import { useAnalyticsQuery } from "./useAnalyticsQuery";

export const useHeatmapData = ({
  timeRange,
  queryType,
  groupBy,
}: HeatmapQueryParams): HeatmapData => {
  // 查询参数
  const queryParams = useMemo(
    () => ({
      queryType,
      params: {
        start: timeRange.start,
        end: timeRange.end,
        page: 1,
        page_size: 100,
      },
    }),
    [timeRange, queryType],
  );

  // 执行查询
  const query = useAnalyticsQuery(queryParams);

  // 处理数据
  const processedData = useMemo(() => {
    const defaultData: HeatmapData = {
      data: [],
      isLoading: query.isLoading,
      error: query.error as Error | undefined,
    };

    if (!query.data) {
      return defaultData;
    }

    if (groupBy === "region") {
      // 处理地区数据
      const topIpsData = query.data as IByTopSourceIpsResponseItem;

      // 按region分组并汇总数据
      const regionGroups = topIpsData.reduce(
        (acc, item) => {
          if (!item.src_region) return acc;

          if (!acc[item.src_region]) {
            acc[item.src_region] = {
              totalBytes: 0,
              totalPackets: 0,
              ips: new Set<string>(),
            };
          }

          acc[item.src_region].totalBytes += item.total_bytes;
          acc[item.src_region].totalPackets += item.total_packets;
          acc[item.src_region].ips.add(item.ip);

          return acc;
        },
        {} as Record<
          string,
          {
            totalBytes: number;
            totalPackets: number;
            ips: Set<string>;
          }
        >,
      );

      // 转换为热力图数据格式
      return {
        ...defaultData,
        data: Object.entries(regionGroups)
          .map(([region, stats]) => {
            const bytes = bytesToSize(stats.totalBytes);
            return {
              id: region,
              value: parseFloat(bytes.size.toString()),
              metadata: {
                region: region,
                ips: Array.from(stats.ips),
                totalPackets: stats.totalPackets,
                totalBytes: stats.totalBytes,
              },
            };
          })
          .sort((a, b) => b.value - a.value),
      };
    }

    if (groupBy === "protocol") {
      // 处理协议分布数据
      const protocolData = query.data as IProtocolDistributionResponseRecord;
      return {
        ...defaultData,
        data: protocolData.distribution.map((item) => ({
          id: item.protocol || "Unknown",
          value: item.percentage_bytes || 0,
          metadata: {
            protocol: item.protocol,
            packetCount: item.packet_count,
            totalBytes: item.total_bytes,
          },
        })),
      };
    }

    return defaultData;
  }, [query.data, query.isLoading, query.error, groupBy]);

  return processedData;
};
