import { TPieData, TPolyLineData, TRadialBarData, TSmoothLineData } from "./client/types";

export const polylineData:TPolyLineData[] = [
  { timestamp: 1698768000, value: 100, name: "Point 1" },
  { timestamp: 1698771600, value: 380, name: "Point 2" },
  { timestamp: 1698775200, value: 251, name: "Point 3" },
];

export const smoothLineData:TSmoothLineData[] = [
  { timestamp: 1698768000, value: 100, name: "Point 1" },
  { timestamp: 1698771600, value: 380, name: "Point 2" },
  { timestamp: 1698775200, value: 251, name: "Point 3" },
];

export const radialBarData:TRadialBarData[] = [
  { name: "A", value: 80, fill: "#8884d8" },
  { name: "B", value: 50, fill: "#82ca9d" },
  { name: "C", value: 30, fill: "#ffc658" },
];

export const pieData:TPieData[] = [
  { name: "A", value: 40, fill: "#8884d8" },
  { name: "B", value: 30, fill: "#82ca9d" },
  { name: "C", value: 30, fill: "#ffc658" },
];
