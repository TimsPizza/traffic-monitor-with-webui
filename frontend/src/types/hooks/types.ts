import { ApiError } from "../../client/api/models/base";
import { TQueryType } from "../../client/types";
import { TimeRange } from "../../components/TimeRangeSelector";

// Common types
export interface BaseQueryParams {
  timeRange: TimeRange;
  queryType: TQueryType;
  protocol?: string;  // 添加可选的protocol字段
}

export interface BaseQueryResponse {
  isLoading: boolean;
  error?: Error | ApiError | null;
}

// Card types
export interface ProtocolCardQueryParams extends BaseQueryParams {
  compareWithPrevious?: boolean;
}

export interface ProtocolCardData extends BaseQueryResponse {
  current: {
    value: number;
    label: string;
    secondaryValue?: number;
  };
  trend?: number;
}

// Chart types
export type ChartType = 'trend' | 'distribution';

export interface ChartQueryParams extends BaseQueryParams {
  chartType: ChartType;
  interval?: number;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  timestamp?: number;
}

export interface ChartData extends BaseQueryResponse {
  data: ChartDataPoint[];
}

// Heatmap types
export type GroupByType = 'region' | 'protocol';

export interface HeatmapQueryParams extends BaseQueryParams {
  groupBy: GroupByType;
}

export interface HeatmapDataPoint {
  id: string;
  value: number;
  metadata?: Record<string, any>;
}

export interface HeatmapData extends BaseQueryResponse {
  data: HeatmapDataPoint[];
}
