import { useMemo } from "react";
import { Col, Row } from "react-bootstrap";
import {
  IProtocolDistribution,
  ITimeSeries,
} from "../client/api/models/request";
import {
  IProtocolDistributionResponse,
  IProtocolDistributionResponseRecord,
  ITimeSeriesResponse,
} from "../client/api/models/response";
import {
  DEFAULT_COLOR_PALETTES,
  EChartType,
  TPieData,
  TPolyLineData,
} from "../client/types";
import Card, { ICardData } from "../components/Card";
import Chart from "../components/Chart";
import { smoothLineData } from "../fakedata";
import { useAnalyticsQuery } from "../hooks/useAnalyticsQuery";
import { unix2DateString } from "../utils/timetools";
import {
  bytesToSize,
  getProtocolDistributionRecordByProtocol,
} from "../utils/tools";

const now = Date.now() / 1e3;
const currentDayQueryParams = {
  queryType: "protocolDistribution" as const,
  params: {
    start: now - 86400,
    end: now,
    page: 1,
    page_size: 10,
  },
};

const previousDayQueryParams = {
  queryType: "protocolDistribution" as const,
  params: {
    start: now - 86400 * 2,
    end: now - 86400,
    page: 1,
    page_size: 10,
  },
};

const timeSeriesQueryParams = {
  queryType: "timeSeries" as const,
  params: {
    start: Date.now() / 1e3 - 86400 * 7,
    end: Date.now() / 1e3,
    interval: 86400,
    page: 1,
    page_size: 10,
  },
};

const calculateTrend = (
  current?: number,
  previous?: number,
): number | undefined => {
  if (current === undefined || previous === undefined || previous === 0) {
    return undefined;
  }
  return ((current - previous) / previous) * 100;
};

interface IProtocolStats {
  packets: number;
  total: string;
  bytes: number;
}

const getProtocolStats = (
  protocol: string,
  data: any,
): IProtocolStats | null => {
  const record = getProtocolDistributionRecordByProtocol(protocol, data);
  if (!record) return null;

  const rec = bytesToSize(record.total_bytes);
  return {
    packets: record.packet_count,
    total: `${rec.size} ${rec.unit}`,
    bytes: record.total_bytes,
  };
};

const buildCardDataByProtocolName = (
  protocol: string,
  currentStats: IProtocolStats | null,
  previousStats: IProtocolStats | null,
): ICardData["data"] => {
  if (!currentStats) {
    return {
      packets: 0,
      total: "0 B",
    };
  }

  return {
    packets: currentStats.packets,
    total: currentStats.total,
    trend: calculateTrend(currentStats.bytes, previousStats?.bytes),
  };
};

const buildPieDataByProtocolName = (protocol: string, obj: any): TPieData => {
  const record = getProtocolDistributionRecordByProtocol(protocol, obj)!;
  return {
    name: protocol,
    value: record.percentage_bytes,
  };
};

const Dashboard = () => {
  const currentDayQuery = useAnalyticsQuery<
    IProtocolDistribution,
    IProtocolDistributionResponse
  >(currentDayQueryParams);

  const previousDayQuery = useAnalyticsQuery<
    IProtocolDistribution,
    IProtocolDistributionResponse
  >(previousDayQueryParams);

  const timeSeriesQuery = useAnalyticsQuery<ITimeSeries, ITimeSeriesResponse>(
    timeSeriesQueryParams,
  );

  const cardData = useMemo(() => {
    if (!currentDayQuery.data) return null;

    const protocols = ["HTTPS", "HTTP", "SSH", "Unknown"] as const;
    const result: Record<(typeof protocols)[number], ICardData["data"]> =
      {} as any;

    protocols.forEach((protocol) => {
      const currentStats = getProtocolStats(protocol, currentDayQuery.data);
      const previousStats = previousDayQuery.data
        ? getProtocolStats(protocol, previousDayQuery.data)
        : null;

      result[protocol] = buildCardDataByProtocolName(
        protocol,
        currentStats,
        previousStats,
      );
    });

    return result;
  }, [currentDayQuery.data, previousDayQuery.data]);

  const lineChartData = useMemo(() => {
    if (!timeSeriesQuery.data) return [];
    // supress ts error
    if (!Array.isArray(timeSeriesQuery.data)) {
      return;
    }
    const resp: TPolyLineData[] = [];
    console.log(timeSeriesQuery.data);
    timeSeriesQuery.data.forEach((item) => {
      resp.push({
        name: unix2DateString(item.time_range.start),
        value: parseInt(bytesToSize(item.total_bytes).size as string),
        timestamp: item.time_range.start,
      });
    });
    return resp.sort((a, b) => a.timestamp - b.timestamp);
  }, [timeSeriesQuery.data]);

  const pieChartData = useMemo(() => {
    if (!currentDayQuery.data || currentDayQuery.data.length === 0) return [];
    console.log(currentDayQuery.data);
    const data = currentDayQuery.data as IProtocolDistributionResponseRecord;
    const resp: TPieData[] = [];
    const keys = data.distribution.map((item) => item.protocol);
    keys.forEach((key) => {
      const item = buildPieDataByProtocolName(key, data);
      // @ts-ignore
      if (item.value < 1) return;
      resp.push(item);
    });
    return resp;
  }, [currentDayQuery.data]);

  return (
    <div id="dashboard-wrapper" className="mx-8 h-full rounded-md ">
      <Row className="mt-2 px-2">
        <Col md={12} lg={6} className="mb-2 p-4">
          <Chart
            chartType={EChartType.SMOOTH_LINE}
            title="7 Days Traffic Summary"
            data={lineChartData ?? []}
            placeholder={
              currentDayQuery.isLoading ? (
                <span>Loading...</span>
              ) : (
                <span>No data</span>
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
        </Col>
        <Col md={12} lg={6} className="mb-2 p-4">
          <Chart
            chartType={EChartType.RING}
            title="Ditribution of Protocols (24h)"
            data={pieChartData}
            colorPalette={DEFAULT_COLOR_PALETTES[3]}
            placeholder={
              currentDayQuery.isLoading ? (
                <span className="text-xl">Loading...</span>
              ) : (
                <span className="text-xl">No recent data</span>
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
          />
        </Col>
        <Col md={12} lg={6} className="mb-2 p-4">
          <Row className="">
            <Col lg={4} className="h-full">
              <Card
                title="HTTPS"
                color="from-emerald-500 to-emerald-600"
                data={{
                  loading:
                    currentDayQuery.isLoading || previousDayQuery.isLoading,
                  data: cardData?.HTTPS ?? { packets: 0, total: "0 B" },
                }}
              />
            </Col>
            <Col lg={4} className="h-full">
              <Card
                title="HTTP"
                color="from-blue-500 to-blue-600"
                data={{
                  loading:
                    currentDayQuery.isLoading || previousDayQuery.isLoading,
                  data: cardData?.HTTP ?? { packets: 0, total: "0 B" },
                }}
              />
            </Col>
            <Col lg={4} className="h-full">
              <Card
                title="SSH"
                color="from-violet-500 to-violet-600"
                data={{
                  loading:
                    currentDayQuery.isLoading || previousDayQuery.isLoading,
                  data: cardData?.SSH ?? { packets: 0, total: "0 B" },
                }}
              />
            </Col>
            <Col lg={4} className="mt-4 h-full">
              <Card
                title="Unknown"
                color="from-gray-500 to-gray-600"
                data={{
                  loading:
                    currentDayQuery.isLoading || previousDayQuery.isLoading,
                  data: cardData?.Unknown ?? { packets: 0, total: "0 B" },
                }}
              />
            </Col>
          </Row>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
