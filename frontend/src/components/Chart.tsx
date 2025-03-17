import React from "react";
import { ChartProps, EChartType } from "../types/charts/types";
import PieChart from "./common/Charts/PieChart";
import RingChart from "./common/Charts/RingChart";
import AreaChart from "./common/Charts/AreaChart";
import PolyLineChart from "./common/Charts/PolyLineChart";

const Chart: React.FC<Partial<ChartProps>> = (props) => {
  const { chartType } = props;

  switch (chartType) {
    case EChartType.PIE:
      return <PieChart {...props} />;
    case EChartType.RING:
      return <RingChart {...props} />;
    case EChartType.POLY_LINE:
      return <PolyLineChart {...props} />;
    case EChartType.SMOOTH_LINE:
      return <PolyLineChart {...props} />;
    default:
      return <AreaChart {...props} />;
  }
};

export default Chart;
