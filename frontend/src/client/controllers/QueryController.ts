import { QueryService } from '../services/services';
import { IAccessRecord } from '../models/models';
import { TQueryParams, TQueryType } from '../types';

export class QueryController {
  public static async queryPackets(
    type: TQueryType,
    params: TQueryParams
  ): Promise<IAccessRecord[]> {
    try {
      const records = await QueryService.queryPackets(type, params);
      return records;
    } catch (error) {
      throw new Error(`Failed to query ${type} packets`);
    }
  }
}
