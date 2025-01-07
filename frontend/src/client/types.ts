// Type definitions for charts

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
  fill: string;
};

export type TSmoothLineData = TPolyLineData;

export type TColorPalette = string[];

export const DEFAULT_COLOR_PALETTES: TColorPalette[] = [
  ["#16C47F", "#FFD65A", "#FF9D23", "#F93827"],
  ["#FF9D23", "#FFD65A", "#16C47F", "#F93827"],
  ["#FFD65A", "#16C47F", "#FF9D23", "#F93827"],
  ["#F93827", "#FFD65A", "#FF9D23", "#16C47F"],
  ["#FB4141", "#FFC145", "#ECE852", "#5CB338"],
  ["FF8383", "#FFF574", "#A1D6CB", "#A19AD3"],
];

// End of type definitions for charts

export const DATE_FORMATTERS = {
  YYYY: { year: "numeric" },
  YYYY_MM: { year: "numeric", month: "2-digit" },
  YYYY_MM_DD: { year: "numeric", month: "2-digit", day: "2-digit" },
  YYYY_MM_DD__HH_mm: {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  },
  YYYY_MM_DD__HH_mm_ss: {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  },
  MM_DD: { month: "2-digit", day: "2-digit" },
  MM_DD__HH_mm: {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  },
  HH_mm: { hour: "2-digit", minute: "2-digit", hour12: false },
  HH_mm_ss: {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  },
} as const;
