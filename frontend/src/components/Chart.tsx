import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  RadialBarChart,
  RadialBar,
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
  TRadialBarData,
  DATE_FORMATTERS,
} from "../client/types";
import { unix2Date } from "../utils/timetools";

interface ChartProps {
  chartType: EChartType;
  data: TChartData[];
  title: string | null;
  colorPalette?: TColorPalette;
}

const Chart: React.FC<ChartProps> = ({
  title,
  data,
  chartType,
  colorPalette = DEFAULT_COLOR_PALETTES[0],
}) => {
  const [titleColor, setTitleColor] = useState(colorPalette[0]);
  useEffect(() => {
    console.log("type: ", chartType, "color: ", colorPalette);
  }, []);
  const renderChart = () => {
    let currentColorIndex = 0;
    const getRndColor = () => {
      currentColorIndex += 1;
      console.log("getRndColor: ", currentColorIndex % colorPalette.length);
      return colorPalette[currentColorIndex % colorPalette.length];
    };

    switch (chartType) {
      case EChartType.POLY_LINE:
        return (
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={getRndColor()} stopOpacity={0.8} />
                <stop
                  offset="95%"
                  stopColor={getRndColor()}
                  stopOpacity={0.2}
                />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(timestamp) =>
                unix2Date(timestamp, DATE_FORMATTERS.HH_mm)
              }
            />
            <YAxis />
            <Tooltip />
            <Area
              type="linear"
              dataKey="value"
              stroke={getRndColor()}
              fill="url(#colorGradient)"
            />
            {/* <Legend /> */}
            <Line type="linear" dataKey="value" stroke={getRndColor()} />
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
                <stop offset="5%" stopColor={getRndColor()} stopOpacity={0.8} />
                <stop offset="95%" stopColor={getRndColor()} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(timestamp) =>
                unix2Date(timestamp, DATE_FORMATTERS.HH_mm)
              }
            />
            <YAxis />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="value"
              stroke={getRndColor()}
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
              {(data as TPieData[]).map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={getRndColor()}
                  style={{
                    filter: `drop-shadow(0px 0px 5px ${colorPalette[index % colorPalette.length]}`,
                  }}
                />
              ))}
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
              color={getRndColor()}
              // outerRadius={100}
              fill={getRndColor()}
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
      className={`flex h-full w-full flex-col rounded-md border border-gray-300`}
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
