import { IFullAccessRecordResponse } from "../api/models/response";
import { QueryService } from "../services/query";
import { TQueryParams } from "../types";
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

type TQueryType = 
  | 'bySourceIP'
  | 'byProtocol' 
  | 'byTimeRange'
  | 'byDestinationPort'
  | 'bySourceRegion'
  | 'protocolDistribution'
  | 'trafficSummary'
  | 'timeSeries'
  | 'topSourceIPs';

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
