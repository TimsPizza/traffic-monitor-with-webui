import React, { useState } from "react";
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
import { unix2Date } from "../utils/timetools";

interface ChartProps {
  chartType: EChartType;
  data: TChartData[];
  title: string | null;
  colorPalette?: TColorPalette;
  bordered?: boolean;
}

const Chart: React.FC<ChartProps> = ({
  title,
  data,
  chartType,
  colorPalette = DEFAULT_COLOR_PALETTES[0],
  bordered = true,
}) => {
  // color palette usage
  const backgroundColor = "#F3F4F6";
  const titleColor = colorPalette[0];
  const primaryFill = colorPalette[1];
  const secondaryFill = colorPalette[2];
  const accentColor = colorPalette[3];
  const borderColor = "#0000004B";
  const gradientColorStart = "#0062ff";
  // const gradientColorMiddle = "	#61efff";
  const gradientColorEnd = "#ffffff";

  const renderChart = () => {
    switch (chartType) {
      case EChartType.POLY_LINE:
        return (
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="0%"
                  stopColor={gradientColorStart}
                  stopOpacity={0.9}
                />
                <stop
                  offset="65%"
                  stopColor={gradientColorStart}
                  stopOpacity={0.4}
                />
                <stop
                  offset="100%"
                  stopColor={gradientColorEnd}
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={borderColor} />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(timestamp) =>
                unix2Date(timestamp, DATE_FORMATTERS.HH_mm)
              }
              stroke={borderColor}
            />
            <YAxis stroke={borderColor} />
            <Tooltip />
            <Area
              type="linear"
              dataKey="value"
              stroke={accentColor}
              fill="url(#colorGradient)"
            />
            <Line type="linear" dataKey="value" stroke={accentColor} />
          </AreaChart>
        );

      case EChartType.SMOOTH_LINE:
        return (
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={primaryFill} stopOpacity={0.8} />
                <stop offset="50%" stopColor={primaryFill} stopOpacity={0.5} />
                <stop offset="100%" stopColor={secondaryFill} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={borderColor} />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(timestamp) =>
                unix2Date(timestamp, DATE_FORMATTERS.HH_mm)
              }
              stroke={borderColor}
            />
            <YAxis stroke={borderColor} />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="value"
              stroke={accentColor}
              fill="url(#colorGradient)"
            />
          </AreaChart>
        );

      case EChartType.RING:
        return (
          <PieChart>
            <Pie
              data={data as TPieData[]}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius="60%"
              outerRadius="80%"
              startAngle={90}
              endAngle={-270}
            >
              {(data as TPieData[]).map((entry, index) => {
                const colorIndex = index % colorPalette.length;
                return (
                  <Cell
                    key={`cell-${index}`}
                    fill={colorPalette[colorIndex]}
                    style={{
                      filter: `drop-shadow(0px 0px 5px ${accentColor})`,
                    }}
                  />
                );
              })}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        );

      case EChartType.PIE:
        return (
          <PieChart margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <Pie
              data={data as TPieData[]}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              color={accentColor}
              fill={primaryFill}
              label
            />
            <Tooltip />
            <Legend />
          </PieChart>
        );

      default:
        return null;
    }
  };

  return (
    <div
      className={`flex h-full w-full flex-col`}
      style={{
        backgroundColor: backgroundColor,
        border: bordered ? `1px solid ${borderColor}` : "none",
        borderRadius: bordered ? "0.375rem" : "0",
      }}
    >
      {title && (
        <h2
          className={`p-1 text-center text-xl font-bold`}
          style={{ color: titleColor }}
        >
          {title}
        </h2>
      )}
      <ResponsiveContainer minHeight={150} width={"100%"}>
        {renderChart() || <>undefined</>}
      </ResponsiveContainer>
    </div>
  );
};

export default Chart;
