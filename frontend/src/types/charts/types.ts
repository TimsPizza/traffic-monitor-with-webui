// Type definitions for charts

import { DATE_FORMATTERS } from "../formats/types";

export enum EChartType {
  RING = "ring",
  POLY_LINE = "poly-line",
  PIE = "pie",
  SMOOTH_LINE = "smooth-line",
}

export type TChartData =
  | TRadialBarData
  | TPolyLineData
  | TPieData
  | TSmoothLineData;

export type TChartDataBase = {
  name: string; // data name for x-axis display
  value: number;
};
export type TRadialBarData = TChartDataBase & {
  fill: string;
};

export type TPolyLineData = TChartDataBase & {
  timestamp: number;
};

export type TPieData = TChartDataBase & {
  fill?: string;
};

export type TSmoothLineData = TPolyLineData;

export type TColorPalette = string[];

/**
 * 定义标准颜色调色板
 * 每个调色板包含6种颜色，用于不同UI元素：
 * 0: 标题颜色 (Title color)
 * 1: 主要填充色 (Primary fill color)
 * 2: 次要填充色 (Secondary fill color)
 * 3: 强调色 (Accent color)
 * 4: 背景色 (Background color)
 * 5: 边框/分割线颜色 (Border/Divider color)
 */
export const DEFAULT_COLOR_PALETTES: TColorPalette[] = [
  // 现代UI调色板 (Modern UI palette)
  ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#f3f4f6", "#e5e7eb"],

  // 深色主题调色板 (Dark theme palette)
  ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#1f2937", "#374151"],

  // 柔和色调调色板 (Pastel palette)
  ["#93c5fd", "#6ee7b7", "#fcd34d", "#fca5a5", "#f9fafb", "#e5e7eb"],

  // 高对比度调色板 (High contrast palette)
  ["#2563eb", "#059669", "#d97706", "#dc2626", "#ffffff", "#d1d5db"],

  // 色盲友好调色板 (Colorblind-friendly palette)
  ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#f7f7f7", "#cccccc"],
];

export interface ChartStyleOptions {
  showYAxis?: boolean;
  showXAxis?: boolean;
  showGrid?: boolean;
  showLegend?: boolean;
  showTooltip?: boolean;
  yAxisWidth?: number;
  gridStroke?: string;
  gridStrokeDasharray?: string;
}

export interface ChartDataOptions {
  dateFormatter?: keyof typeof DATE_FORMATTERS;
  timezone?: string;
  areaOpacity?: number;
  strokeWidth?: number;
}

export interface ChartProps {
  chartType: EChartType;
  data: TChartData[];
  title?: string;
  colorPalette?: TColorPalette;
  style?: ChartStyleOptions;
  dataOptions?: ChartDataOptions;
  className?: string;
  placeholder?: React.ReactNode;
  children: React.ReactElement;
}

// End of type definitions for charts
