import { ResponsiveContainer } from "recharts";
import {
  ChartDataOptions,
  ChartProps,
  ChartStyleOptions,
  DEFAULT_COLOR_PALETTES,
} from "../../../types/charts/types";

const defaultStyleOptions: ChartStyleOptions = {
  showYAxis: false,
  showXAxis: true,
  showGrid: false,
  showLegend: false,
  showTooltip: true,
  yAxisWidth: 20,
  gridStroke: "rgba(0, 0, 0, 0.1)",
  gridStrokeDasharray: "4 4",
};

const defaultDataOptions: ChartDataOptions = {
  dateFormatter: "MM_DD",
  timezone: "GMT+8",
  areaOpacity: 0.15,
  strokeWidth: 2,
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

const Chart: React.FC<ChartProps> = ({
  title,
  data,
  chartType,
  colorPalette = DEFAULT_COLOR_PALETTES[0],
  style = defaultStyleOptions,
  dataOptions = defaultDataOptions,
  className = "",
  placeholder,
  children,
}) => {
  const titleColor = colorPalette[0];
  const primaryFill = colorPalette[1];
  const secondaryFill = colorPalette[2];
  const accentColor = colorPalette[3];

  // 合并默认选项
  const finalStyle = { ...defaultStyleOptions, ...style };
  const finalDataOptions = { ...defaultDataOptions, ...dataOptions };

  return (
    <div
      className={`flex h-full w-full flex-col rounded-xl border border-gray-100/20 bg-white/50 backdrop-blur-sm transition-all duration-300 dark:!bg-gray-800 ${className}`}
    >
      {title && (
        <div className="top-0 border-b border-gray-100/20 px-4 py-2">
          <h2
            className="text-lg font-semibold tracking-wide"
            style={{ color: titleColor }}
          >
            {title}
          </h2>
        </div>
      )}
      {data.length === 0 ? (
        <div className="relative flex h-full min-h-[300px] w-full flex-1 items-center justify-center dark:text-gray-50">
          {placeholder}
        </div>
      ) : (
        <div className="relative h-full w-full flex-1">
          <ResponsiveContainer
            width="100%"
            height="100%"
            minHeight={300}
            debounce={50}
          >
            {children}
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default Chart;
