const DATE_FORMAT_OPTIONS = {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
} as const;

export type TTimezone =
  | "GMT"
  | "GMT+0"
  | "GMT+1"
  | "GMT+2"
  | "GMT+3"
  | "GMT+4"
  | "GMT+5"
  | "GMT+6"
  | "GMT+7"
  | "GMT+8"
  | "GMT+9"
  | "GMT+10"
  | "GMT+11"
  | "GMT+12"
  | "GMT-1"
  | "GMT-2"
  | "GMT-3"
  | "GMT-4"
  | "GMT-5"
  | "GMT-6"
  | "GMT-7"
  | "GMT-8"
  | "GMT-9"
  | "GMT-10"
  | "GMT-11"
  | "GMT-12";

export type TIanaTimezone =
  | "UTC"
  | "Etc/GMT-1"
  | "Etc/GMT-2"
  | "Etc/GMT-3"
  | "Etc/GMT-4"
  | "Etc/GMT-5"
  | "Etc/GMT-6"
  | "Etc/GMT-7"
  | "Etc/GMT-8"
  | "Etc/GMT-9"
  | "Etc/GMT-10"
  | "Etc/GMT-11"
  | "Etc/GMT-12"
  | "Etc/GMT+1"
  | "Etc/GMT+2"
  | "Etc/GMT+3"
  | "Etc/GMT+4"
  | "Etc/GMT+5"
  | "Etc/GMT+6"
  | "Etc/GMT+7"
  | "Etc/GMT+8"
  | "Etc/GMT+9"
  | "Etc/GMT+10"
  | "Etc/GMT+11"
  | "Etc/GMT+12";

export const GMT_TO_IANA: Record<TTimezone, TIanaTimezone> = {
  GMT: "UTC",
  "GMT+0": "UTC",
  "GMT+1": "Etc/GMT-1",
  "GMT+2": "Etc/GMT-2",
  "GMT+3": "Etc/GMT-3",
  "GMT+4": "Etc/GMT-4",
  "GMT+5": "Etc/GMT-5",
  "GMT+6": "Etc/GMT-6",
  "GMT+7": "Etc/GMT-7",
  "GMT+8": "Etc/GMT-8",
  "GMT+9": "Etc/GMT-9",
  "GMT+10": "Etc/GMT-10",
  "GMT+11": "Etc/GMT-11",
  "GMT+12": "Etc/GMT-12",
  "GMT-1": "Etc/GMT+1",
  "GMT-2": "Etc/GMT+2",
  "GMT-3": "Etc/GMT+3",
  "GMT-4": "Etc/GMT+4",
  "GMT-5": "Etc/GMT+5",
  "GMT-6": "Etc/GMT+6",
  "GMT-7": "Etc/GMT+7",
  "GMT-8": "Etc/GMT+8",
  "GMT-9": "Etc/GMT+9",
  "GMT-10": "Etc/GMT+10",
  "GMT-11": "Etc/GMT+11",
  "GMT-12": "Etc/GMT+12",
};

// convert unix timestamp to date string with timezone support
export const unix2Date = (
  unix: number,
  timezone: TTimezone = "GMT+8",
): string => {
  const date = new Date(unix * 1000);
  const ianaTimeZone = GMT_TO_IANA[timezone]; // 将 GMT 时区转换为 IANA 时区

  return new Intl.DateTimeFormat("zh-CN", {
    ...DATE_FORMAT_OPTIONS,
    timeZone: ianaTimeZone,
  }).format(date);
};

export const date2Unix = (date: string) => {
  if (!isValidDateStr(date)) {
    throw new Error("Invalid date string");
  }
  return new Date(date).getTime() / 1000;
};

export const isValidDateStr = (dateStr: string) => {
  const reg = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/; // YYYY-MM-DD HH:MM:SS
  return reg.test(dateStr);
};

export const getLocalTimezone = (): TTimezone => {
  const offset = new Date().getTimezoneOffset();
  const offsetHours = offset / 60;
  return (
    offsetHours >= 0 ? `GMT-${offsetHours}` : `GMT+${Math.abs(offsetHours)}`
  ) as TTimezone;
};
