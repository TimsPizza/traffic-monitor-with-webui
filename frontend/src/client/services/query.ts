import {
  IByProtocolResponse,
  IByDestinationPortResponse,
  IByTimeRangeResponse,
  IByRegionResponse as IBySourceRegionResponse,
  IBySourceIPResponse,
  ITrafficSummaryResponse,
  ITimeSeriesResponse,
  IProtocolAnalysisResponse,
  IProtocolDistributionResponse,
  IByTopSourceIpsResponse,
} from "../api/models/response";
import {
  IBySourceIP,
  IByProtocol,
  IByTimeRange,
  IByDestinationPort,
  IBySourceRegion,
  IProtocolDistribution,
  ITrafficSummary,
  ITimeSeries,
  IProtocolAnalysis,
  IByTopSourceIps,
} from "../api/models/request";
import { DataApi } from "../api/requests";

export class QueryService {
  private static queryMethods = {
    'bySourceIP': QueryService.queryBySourceIP,
    'byProtocol': QueryService.queryByProtocol,
    'byTimeRange': QueryService.queryByTimeRange,
    'byDestinationPort': QueryService.queryByDestinationPort,
    'bySourceRegion': QueryService.queryBySourceRegion,
    'protocolDistribution': QueryService.queryProtocolDistribution,
    'trafficSummary': QueryService.queryTrafficSummary,
    'timeSeries': QueryService.queryTimeSeries,
    'protocolAnalysis': QueryService.queryProtocolAnaysis,
    'topSourceIPs': QueryService.queryTopSourceIPs,
  };

  public static async query<TRequest extends object, TResponse>(
    type: keyof typeof QueryService.queryMethods,
    payload: TRequest
  ): Promise<TResponse> {
    const method = QueryService.queryMethods[type];
    if (!method) {
      throw new Error(`Invalid query type: ${type}`);
    }
    return method(payload as any) as Promise<TResponse>;
  }

  public static async queryBySourceIP(
    config: IBySourceIP,
  ): Promise<IBySourceIPResponse> {
    return DataApi.getBySourceIP(config);
  }

  public static async queryByProtocol(
    config: IByProtocol,
  ): Promise<IByProtocolResponse> {
    return DataApi.getByProtocol(config);
  }

  public static async queryByTimeRange(
    config: IByTimeRange,
  ): Promise<IByTimeRangeResponse> {
    return DataApi.getByTimeRange(config);
  }

  public static async queryByDestinationPort(
    config: IByDestinationPort,
  ): Promise<IByDestinationPortResponse> {
    return DataApi.getByDestinationPort(config);
  }

  public static async queryBySourceRegion(
    config: IBySourceRegion,
  ): Promise<IBySourceRegionResponse> {
    return DataApi.getBySourceRegion(config);
  }

  public static async queryProtocolDistribution(
    config: IProtocolDistribution,
  ): Promise<IProtocolDistributionResponse> {
    return DataApi.getProtocolDistribution(config);
  }

  public static async queryTrafficSummary(
    config: ITrafficSummary,
  ): Promise<ITrafficSummaryResponse> {
    return DataApi.getTrafficSummary(config);
  }

  public static async queryTimeSeries(
    config: ITimeSeries,
  ): Promise<ITimeSeriesResponse> {
    return DataApi.getTimeSeries(config);
  }

  public static async queryProtocolAnaysis(
    config: IProtocolAnalysis,
  ): Promise<IProtocolAnalysisResponse> {
    return DataApi.getProtocolAnalysis(config);
  }

  public static async queryTopSourceIPs(
    config: IByTopSourceIps,
  ): Promise<IByTopSourceIpsResponse> {
    return DataApi.getTopSourceIPs(config);
  }
}
