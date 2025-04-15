import React, { useMemo } from "react";
import Card from "../components/Card";
import Chart from "../components/Chart";
import WorldMap from "../components/common/Charts/WorldMap";
import TimeRangeSelector, { TimeRange } from "../components/TimeRangeSelector";
import { useChartData, useHeatmapData, useProtocolsData } from "../hooks";
import { DEFAULT_COLOR_PALETTES, EChartType } from "../types/charts/types";
import { WindowSizeContext } from "../App";
import { EMediaBreakpoints } from "../types/ui/types";

const Dashboard = () => {
  // Time range state
  const { breakpoint } = React.useContext(WindowSizeContext);
  const [selectedRange, setSelectedRange] = React.useState<TimeRange>({
    label: "Recent 7 Days",
    start: Date.now() / 1e3 - 86400 * 7,
    end: Date.now() / 1e3,
    interval: 86400, // 1 day
  });

  // Protocols data
  const {
    protocolsData,
    selectedProtocols,
    addProtocol,
    removeProtocol,
    resetProtocols,
    isLoading: protocolsLoading,
  } = useProtocolsData({ timeRange: selectedRange });
  if (!protocolsLoading) {
    console.log("protocolsData:", protocolsData);
  }

  // Traffic trend data
  const trendData = useChartData({
    timeRange: selectedRange,
    queryType: "timeSeries",
    chartType: "trend",
    interval: selectedRange.interval,
  });

  // Geographic distribution data
  const geoData = useHeatmapData({
    timeRange: selectedRange,
    queryType: "topSourceIPs",
    groupBy: "region",
  });

  // Last update time
  const lastUpdateTime = useMemo(() => {
    return new Date().toLocaleTimeString();
  }, [selectedRange]);

  // Handle time range change
  const handleTimeRangeChange = (range: TimeRange) => {
    setSelectedRange(range);
  };

  return (
    <div
      className={`mx-auto max-w-7xl ${breakpoint >= EMediaBreakpoints.lg ? "px-4 py-6" : ""}`}
    >
      {/* Section 1: Protocol Statistics */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
            协议流量统计
          </h2>
          <div className="flex items-center gap-4">
            <button
              onClick={resetProtocols}
              className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
            >
              重置默认协议
            </button>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              最后更新: {lastUpdateTime}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {protocolsData &&
            protocolsData.map(({ protocol, loading, current, trend }) => (
              <Card
                key={protocol}
                title={protocol}
                color={
                  protocol === "HTTPS"
                    ? "from-emerald-500 to-emerald-600"
                    : protocol === "HTTP"
                      ? "from-blue-500 to-blue-600"
                      : protocol === "SSH"
                        ? "from-violet-500 to-violet-600"
                        : "from-gray-500 to-gray-600"
                }
                data={{
                  loading,
                  data: {
                    packets: current.secondaryValue || 0,
                    total: `${current.value} ${current.label}`,
                    trend,
                  },
                }}
              />
            ))}
        </div>
      </div>

      {/* Section 2: Traffic Trend */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
            流量趋势
          </h2>
          <TimeRangeSelector
            value={selectedRange}
            onChange={handleTimeRangeChange}
            loading={trendData.isLoading}
          />
        </div>
        <div className="rounded-lg bg-white dark:bg-gray-800">
          <Chart
            chartType={EChartType.SMOOTH_LINE}
            title={`流量趋势 (${selectedRange.label})`}
            data={trendData.data}
            placeholder={
              trendData.isLoading ? (
                <span>加载中...</span>
              ) : (
                <span>暂无数据</span>
              )
            }
            style={{
              showXAxis: true,
              showYAxis: true,
              showGrid: true,
              showLegend: false,
              showTooltip: true,
              yAxisWidth: 30,
              gridStroke: "rgba(0, 0, 0, 0.1)",
              gridStrokeDasharray: "4 4",
            }}
            colorPalette={DEFAULT_COLOR_PALETTES[3]}
          />
        </div>
      </div>

      {/* Section 3: Geographic Distribution */}
      <div className="mb-8">
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
            流量来源地区分布
          </h2>
        </div>
        <div className="min-h-[400px] rounded-lg bg-white dark:bg-gray-800">
          <WorldMap loading={geoData.isLoading} data={geoData.data} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
