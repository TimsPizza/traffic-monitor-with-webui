import React from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  ChartProps,
  DEFAULT_COLOR_PALETTES,
} from "../../../types/charts/types";
import { unix2DateString } from "../../../utils/timetools";
import BaseChart from "./BaseChart";

const PolyLineChart: React.FC<ChartProps> = (props) => {
  const {
    data,
    colorPalette = DEFAULT_COLOR_PALETTES[0],
    style = {},
    dataOptions = {},
    chartType,
  } = props;

  const margin = {
    top: 10,
    right: 20,
    left: style.showYAxis ? style.yAxisWidth || 20 : 20,
    bottom: style.showXAxis ? 25 : 10,
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
    <BaseChart {...props}>
      <LineChart data={data} margin={margin} height={300}>
        {style.showGrid && (
          <CartesianGrid
            strokeDasharray={style.gridStrokeDasharray}
            stroke={style.gridStroke}
            vertical={false}
            opacity={0.5}
          />
        )}

        {style.showXAxis && (
          <XAxis
            dataKey="timestamp"
            tickFormatter={(timestamp) =>
              unix2DateString(timestamp, "MM_DD", dataOptions.timezone as any)
            }
            axisLine={false}
            tickLine={false}
            fontSize={12}
            dy={8}
            tick={{ fill: "#666" }}
            minTickGap={30}
          />
        )}

        {style.showYAxis && (
          <YAxis
            width={style.yAxisWidth || 20}
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

        {style.showTooltip && (
          <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: "#666" }} />
        )}

        {style.showLegend && (
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

        <Line
          type={chartType === "smooth-line" ? "monotone" : "linear"}
          dataKey="value"
          stroke={colorPalette[3]}
          strokeWidth={dataOptions.strokeWidth}
          dot={false}
          isAnimationActive={true}
          animationDuration={1000}
          animationEasing="ease-out"
          connectNulls={true}
        />
      </LineChart>
    </BaseChart>
  );
};

export default PolyLineChart;
