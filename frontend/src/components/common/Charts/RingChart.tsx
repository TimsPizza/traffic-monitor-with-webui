import React from "react";
import { PieChart as ReChartsPie, Pie, Cell, Tooltip, Legend } from "recharts";
import BaseChart from "./BaseChart";
import {
  ChartProps,
  DEFAULT_COLOR_PALETTES,
  TPieData,
} from "../../../types/charts/types";

const tooltipStyle = {
  background: "rgba(255, 255, 255, 0.95)",
  border: "none",
  borderRadius: "8px",
  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
  padding: "8px 12px",
  fontSize: "12px",
};

const RingChart: React.FC<ChartProps> = (props) => {
  const { data, colorPalette = DEFAULT_COLOR_PALETTES[0], style = {} } = props;

  return (
    <BaseChart {...props}>
      <ReChartsPie>
        <Pie
          data={data as TPieData[]}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius="60%"
          outerRadius="80%"
          paddingAngle={2}
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
        {style.showTooltip && <Tooltip contentStyle={tooltipStyle} />}
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
      </ReChartsPie>
    </BaseChart>
  );
};

export default RingChart;
