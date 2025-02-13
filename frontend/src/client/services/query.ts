import { AxiosResponse } from "axios";
import {
  IByDestinationPort,
  IByProtocol,
  IBySourceIP,
  IBySourceRegion,
  IByTimeRange,
  IByTopSourceIps,
  IProtocolAnalysis,
  IProtocolDistribution,
  ITimeSeries,
  ITrafficSummary,
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
  ) {
    const method = QueryService.queryMethods[type];
    if (!method) {
      throw new Error(`Invalid query type: ${type}`);
    }
    //@ts-ignore
    const response = await method(payload as any) as Promise<AxiosResponse<TResponse>>;
    console.log("queryService response:", response);
    return response;
  }

  public static async queryBySourceIP(config: IBySourceIP) {
    return await DataApi.getBySourceIP(config);
  }

  public static async queryByProtocol(config: IByProtocol) {
    return await DataApi.getByProtocol(config);
  }

  public static async queryByTimeRange(config: IByTimeRange) {
    return await DataApi.getByTimeRange(config);
  }

  public static async queryByDestinationPort(config: IByDestinationPort) {
    return await DataApi.getByDestinationPort(config);
  }

  public static async queryBySourceRegion(config: IBySourceRegion) {
    return await DataApi.getBySourceRegion(config);
  }

  public static async queryProtocolDistribution(config: IProtocolDistribution) {
    return await DataApi.getProtocolDistribution(config);
  }

  public static async queryTrafficSummary(config: ITrafficSummary) {
    return await DataApi.getTrafficSummary(config);
  }

  public static async queryTimeSeries(config: ITimeSeries) {
    return await DataApi.getTimeSeries(config);
  }

  public static async queryProtocolAnaysis(config: IProtocolAnalysis) {
    return await DataApi.getProtocolAnalysis(config);
  }

  public static async queryTopSourceIPs(config: IByTopSourceIps) {
    return await DataApi.getTopSourceIPs(config);
  }
}
