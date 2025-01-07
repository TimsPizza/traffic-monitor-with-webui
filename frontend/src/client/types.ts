// Type definitions for charts

export enum EChartType {
  RADIAL_BAR = "radial-bar",
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
  fill: string;
};

export type TSmoothLineData = TPolyLineData;

// End of type definitions for charts
