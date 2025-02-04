import { IAccessRecord } from "./client/models/models";
import {
  DATE_FORMATTERS,
  TPieData,
  TPolyLineData,
  TRadialBarData,
  TSmoothLineData,
} from "./client/types";
import { unix2DateString } from "./utils/timetools";

export const polylineData: TPolyLineData[] = [
  { timestamp: 1698768000, value: 100, name: "Point 1" },
  { timestamp: 1698771600, value: 380, name: "Point 2" },
  { timestamp: 1698775200, value: 251, name: "Point 3" },
];

export const smoothLineData: TSmoothLineData[] = [
  { timestamp: 1698768000, value: 100, name: "Point 1" },
  { timestamp: 1698771600, value: 380, name: "Point 2" },
  { timestamp: 1698775200, value: 251, name: "Point 3" },
];

export const radialBarData: TRadialBarData[] = [
  { name: "A", value: 80, fill: "#8884d8" },
  { name: "B", value: 50, fill: "#82ca9d" },
  { name: "C", value: 30, fill: "#ffc658" },
];

export const pieData: TPieData[] = [
  { name: "A", value: 40, fill: "#8884d8" },
  { name: "B", value: 30, fill: "#82ca9d" },
  { name: "C", value: 30, fill: "#ffc658" },
];

const generateRandomIP = () =>
  Array(4)
    .fill(0)
    .map(() => Math.floor(Math.random() * 256))
    .join(".");

const generateRandomPort = () =>
  Math.floor(Math.random() * (65535 - 1024) + 1024);

const protocols = ["tcp", "udp", "icmp"] as const;
const generateRandomProtocol = () =>
  protocols[Math.floor(Math.random() * protocols.length)];

const regions = [
  "US",
  "CN",
  "RU",
  "CA",
  "BR",
  "AU",
  "IN",
  "JP",
  "DE",
  "FR",
] as const;
const generateRandomIPRegion = () =>
  regions[Math.floor(Math.random() * regions.length)];

const generateAccessRecord = (id: number): IAccessRecord => ({
  id: "ex13opxrmj2",
  length: Math.floor(Math.random() * 1000),
  src_ip: generateRandomIP(),
  region: generateRandomIPRegion(),
  dst_port: generateRandomPort(),
  protocol: generateRandomProtocol(),
  timestamp: unix2DateString(
    Date.now() - Math.random() * 86400000,
    DATE_FORMATTERS.HH_mm_ss,
  ),
});

export const accessRecordData: IAccessRecord[] = Array(50)
  .fill(0)
  .map((_, index) => generateAccessRecord(index + 1));
