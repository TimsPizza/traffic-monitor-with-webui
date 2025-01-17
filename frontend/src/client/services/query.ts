// ...existing code...
import { 
  IFullAccessRecordResponse, 
  IByProtocolResponse, 
  IByDestinationPortResponse, 
  IByTimeRangeResponse, 
  IByRegionResponse as IBySourceRegionResponse, 
  IBySourceIPResponse,
  ITrafficSummaryResponse,
  ITimeSeriesResponse,
  IProtocolAnalysisResponse,
  IProtocolDistributionResponse,
  IByTopSourceIpsResponse
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
  IByTopSourceIps
} from "../api/models/request";
// ...existing code...
export class QueryService {
  public static async queryBySourceIP(
    config: IBySourceIP,
  ): Promise<IBySourceIPResponse[]> {}

  public static async queryByProtocol(
    config: IByProtocol,
  ): Promise<IByProtocolResponse> {}

  public static async queryByTimeRange(
    config: IByTimeRange,
  ): Promise<IByTimeRangeResponse> {}

  public static async queryByDestinationPort(
    config: IByDestinationPort,
  ): Promise<IByDestinationPortResponse> {}

  public static async queryBySourceRegion(
    config: IBySourceRegion,
  ): Promise<IBySourceRegionResponse> {}

  public static async queryProtocolDistribution(
    config: IProtocolDistribution,
  ): Promise<IProtocolDistributionResponse> {}

  public static async queryTrafficSummary(
    config: ITrafficSummary,
  ): Promise<ITrafficSummaryResponse> {}

  public static async queryTimeSeries(
    config: ITimeSeries,
  ): Promise<ITimeSeriesResponse> {}

  public static async queryProtocolAnaysis(
    config: IProtocolAnalysis,
  ): Promise<IProtocolAnalysisResponse> {}

  public static async queryTopSourceIPs(
    config: IByTopSourceIps,
  ): Promise<IByTopSourceIpsResponse[]> {}
}
// ...existing code...