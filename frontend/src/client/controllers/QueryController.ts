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
import { QueryService } from "../services/query";
import { TQueryType } from "../types";

export class QueryController {
  public static async query<
    T1 extends 
      | IBySourceIP
      | IByProtocol
      | IByTimeRange
      | IByDestinationPort
      | IBySourceRegion
      | IProtocolDistribution
      | ITrafficSummary
      | ITimeSeries
      | IProtocolAnalysis
      | IByTopSourceIps,
    T2
  >(
    type: TQueryType,
    payload: T1
  ): Promise<T2> {
    try {
      const records = await QueryService.query<T1, T2>(type, payload);
      return records;
    } catch (error) {
      throw new Error(`Failed to query packets: ${error}`);
    }
  }
}
