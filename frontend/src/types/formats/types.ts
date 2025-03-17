export const DATE_FORMATTERS: Record<TDateFormatters, Intl.DateTimeFormatOptions> = {
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

export type TDateFormatters =
  | "YYYY"
  | "YYYY_MM"
  | "YYYY_MM_DD"
  | "YYYY_MM_DD__HH_mm"
  | "YYYY_MM_DD__HH_mm_ss"
  | "MM_DD"
  | "MM_DD__HH_mm"
  | "HH_mm"
  | "HH_mm_ss";
