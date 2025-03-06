import React from "react";
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Cell,
  Area,
  AreaChart,
} from "recharts";
import {
  DEFAULT_COLOR_PALETTES,
  EChartType,
  TColorPalette,
  TChartData,
  TPieData,
  DATE_FORMATTERS,
} from "../client/types";
import { unix2DateString } from "../utils/timetools";

interface ChartStyleOptions {
  showYAxis?: boolean;
  showXAxis?: boolean;
  showGrid?: boolean;
  showLegend?: boolean;
  showTooltip?: boolean;
  yAxisWidth?: number;
  gridStroke?: string;
  gridStrokeDasharray?: string;
}

interface ChartDataOptions {
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
}

const defaultStyleOptions: ChartStyleOptions = {
  showYAxis: false,
  showXAxis: true,
  showGrid: false,
  showLegend: false,
  showTooltip: true,
  yAxisWidth: 20,
  gridStroke: "rgba(0, 0, 0, 0.1)",
  gridStrokeDasharray: "4 4",
};

const defaultDataOptions: ChartDataOptions = {
  dateFormatter: "MM_DD",
  timezone: "GMT+8",
  areaOpacity: 0.15,
  strokeWidth: 2,
};

const Chart: React.FC<ChartProps> = ({
  title,
  data,
  chartType,
  colorPalette = DEFAULT_COLOR_PALETTES[0],
  style = defaultStyleOptions,
  dataOptions = defaultDataOptions,
  className = "",
  placeholder,
}) => {
  // 配色方案
  const titleColor = colorPalette[0];
  const primaryFill = colorPalette[1];
  const secondaryFill = colorPalette[2];
  const accentColor = colorPalette[3];

  // 合并默认选项
  const finalStyle = { ...defaultStyleOptions, ...style };
  const finalDataOptions = { ...defaultDataOptions, ...dataOptions };

  const renderCartesianChart = (isSmooth: boolean = false) => {
    const margin = {
      top: 10,
      right: 20,
      left: finalStyle.showYAxis
        ? finalStyle.yAxisWidth || defaultStyleOptions.yAxisWidth || 60
        : 20,
      bottom: finalStyle.showXAxis ? 25 : 10,
    };

    const tooltipStyle = {
      background: "rgba(255, 255, 255, 0.95)",
      border: "none",
      borderRadius: "8px",
      boxShadow:
        "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
      padding: "8px 10px",
      fontSize: "12px",
    };

    return (
      <AreaChart data={data} margin={margin} height={300}>
        <defs>
          <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
            <stop
              offset="5%"
              stopColor={primaryFill}
              stopOpacity={
                (finalDataOptions.areaOpacity ||
                  defaultDataOptions.areaOpacity ||
                  0.15) * 1.5
              }
            />
            <stop offset="95%" stopColor={secondaryFill} stopOpacity={0.05} />
          </linearGradient>
        </defs>

        {finalStyle.showGrid && (
          <CartesianGrid
            strokeDasharray={finalStyle.gridStrokeDasharray}
            stroke={finalStyle.gridStroke}
            vertical={false}
            opacity={0.5}
          />
        )}

        {finalStyle.showXAxis && (
          <XAxis
            dataKey="timestamp"
            tickFormatter={(timestamp) =>
              unix2DateString(
                timestamp,
                DATE_FORMATTERS[finalDataOptions.dateFormatter || "MM_DD"],
                finalDataOptions.timezone as any,
              )
            }
            axisLine={false}
            tickLine={false}
            fontSize={12}
            dy={8}
            tick={{ fill: "#666" }}
            minTickGap={30}
          />
        )}

        {finalStyle.showYAxis && (
          <YAxis
            width={
              finalStyle.yAxisWidth || defaultStyleOptions.yAxisWidth || 60
            }
            axisLine={false}
            tickLine={false}
            fontSize={12}
            dx={-8}
            tickFormatter={(value) =>
              value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value
            }
            tick={{ fill: "#666" }}
          />
        )}

        {finalStyle.showTooltip && (
          <Tooltip
            contentStyle={tooltipStyle}
            // formatter={(value) => unix2DateString(value)}
            itemStyle={{ color: "#666" }}
          />
        )}

        {finalStyle.showLegend && (
          <Legend
            wrapperStyle={{
              fontSize: "12px",
              color: "#666",
              marginTop: "10px",
              paddingTop: "10px",
              borderTop: "1px solid rgba(0,0,0,0.1)",
            }}
          />
        )}

        <Area
          type={isSmooth ? "monotone" : "linear"}
          dataKey="value"
          stroke={accentColor}
          strokeWidth={finalDataOptions.strokeWidth}
          fill="url(#colorGradient)"
          isAnimationActive={true}
          animationDuration={1000}
          animationEasing="ease-out"
          connectNulls={true}
        />
      </AreaChart>
    );
  };

  const renderPieChart = (isRing: boolean = false) => {
    const tooltipStyle = {
      background: "rgba(255, 255, 255, 0.95)",
      border: "none",
      borderRadius: "8px",
      boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
      padding: "8px 12px",
      fontSize: "12px",
    };

    return (
      <PieChart>
        <Pie
          data={data as TPieData[]}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius={isRing ? "60%" : "0"}
          outerRadius={isRing ? "80%" : "70%"}
          paddingAngle={isRing ? 2 : 0}
          isAnimationActive={true}
          animationDuration={1000}
          animationEasing="ease-out"
        >
          {(data as TPieData[]).map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={colorPalette[index % colorPalette.length]}
              style={{ filter: "drop-shadow(0 1px 2px rgb(0 0 0 / 0.1))" }}
            />
          ))}
        </Pie>
        {finalStyle.showTooltip && <Tooltip contentStyle={tooltipStyle} />}
        {finalStyle.showLegend && (
          <Legend
            wrapperStyle={{
              fontSize: "12px",
              color: "#666",
              marginTop: "10px",
              paddingTop: "10px",
              borderTop: "1px solid rgba(0,0,0,0.1)",
            }}
          />
        )}
      </PieChart>
    );
  };

  const renderChart = () => {
    switch (chartType) {
      case EChartType.POLY_LINE:
        return renderCartesianChart(false);
      case EChartType.SMOOTH_LINE:
        return renderCartesianChart(true);
      case EChartType.RING:
        return renderPieChart(true);
      case EChartType.PIE:
        return renderPieChart(false);
      default:
        return null;
    }
  };

  return (
    <div
      className={`flex h-full w-full flex-col rounded-xl border border-gray-100/20 bg-white/50 dark:!bg-gray-800 shadow-lg backdrop-blur-sm transition-all duration-300 hover:shadow-xl ${className}`}
    >
      {title && (
        <div className="top-0 border-b border-gray-100/20 px-4 py-2">
          <h2
            className="text-lg font-semibold tracking-wide"
            style={{ color: titleColor }}
          >
            {title}
          </h2>
        </div>
      )}
      {data.length === 0 ? (
        <div className="min-h-[300px] flex-1 relative flex h-full w-full items-center justify-center">
          {placeholder}
        </div>
      ) : (
        <div className="relative h-full w-full flex-1">
          <ResponsiveContainer
            width="100%"
            height="100%"
            minHeight={300}
            debounce={50}
          >
            {renderChart() || <>undefined</>}
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default Chart;
