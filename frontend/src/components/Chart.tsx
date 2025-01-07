import React from "react";
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
} from "recharts";
import {
  EChartType,
  TChartData,
  TPieData,
  TRadialBarData,
} from "../client/types";

interface ChartProps {
  chartType: EChartType;
  data: TChartData[];
  title: string | null;
  // when inside a card, the chart should be constrained by height instead of width
  constraintBy?: "height" | "width";
  isStandalone?: boolean;
}

const Chart: React.FC<ChartProps> = ({
  title,
  data,
  chartType,
  constraintBy = "width",
  isStandalone = true,
}) => {
  const renderChart = () => {
    switch (chartType) {
      case EChartType.POLY_LINE:
        return (
          <LineChart
            data={data}
            margin={{ top: 10, right: 10, left: -10, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(timestamp) =>
                new Date(timestamp * 1000).toLocaleTimeString()
              }
            />
            <YAxis />
            <Tooltip />
            {/* <Legend /> */}
            <Line type="monotone" dataKey="value" stroke="#8884d8" />
          </LineChart>
        );
      case EChartType.SMOOTH_LINE:
        return (
          <LineChart
            data={data}
            margin={{ top: 10, right: 10, left: -10, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(timestamp) =>
                new Date(timestamp * 1000).toLocaleTimeString()
              }
            />
            <YAxis />
            <Tooltip />
            {/* <Legend /> */}
            <Line
              type="monotone"
              dataKey="value"
              stroke="#8884d8"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        );
      case EChartType.RADIAL_BAR:
        return (
          <RadialBarChart
            // innerRadius="10%"
            // outerRadius="100%"
            data={data as TRadialBarData[]}
            startAngle={180}
            endAngle={0}
            margin={{ top: 10, right: 10, left: 10, bottom: 10 }}
          >
            <RadialBar
              label={{ fill: "#666", position: "insideStart" }}
              dataKey="value"
            />
            <Legend
              iconSize={10}
              layout="vertical"
              verticalAlign="middle"
              align="right"
            />
            <Tooltip />
          </RadialBarChart>
        );
      case EChartType.PIE:
        return (
          <PieChart margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
            <Pie
              data={data as TPieData[]}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              // outerRadius={100}
              fill="#8884d8"
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
      {title && <h2>{title}</h2>}
      <ResponsiveContainer minHeight={150}  width={"100%"}>
        {renderChart() || <>undefined</>}
      </ResponsiveContainer>
    </div>
  );
};

export default Chart;
