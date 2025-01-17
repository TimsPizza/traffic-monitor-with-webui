import {
  IByProtocolResponse,
  IByDestinationPortResponse,
  IByTimeRangeResponse,
  IBySourceRegionResponse,
  IBySourceIPResponse,
  ITrafficSummaryResponse,
  ITimeSeriesResponse,
  IProtocolAnalysisResponse,
  IProtocolDistributionResponse,
  IByTopSourceIpsResponse,
  TAuthResponse,
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
  TSignUpForm,
  TLoginForm,
} from "../api/models/request";
import { apiClient } from "./apiClient";

export class AuthApi {
  private static BASE_URL = "/auth";
  public static login(data: TLoginForm): Promise<TAuthResponse> {
    return apiClient.instance.post(`${AuthApi.BASE_URL}/login`, data);
  }

  public static signup(data: TSignUpForm): Promise<TAuthResponse> {
    return apiClient.instance.post(`${AuthApi.BASE_URL}/signup`, data);
  }

  public static logout(): Promise<void> {
    return apiClient.instance.post(`${AuthApi.BASE_URL}/logout`);
  }

  public static refreshToken(): Promise<TAuthResponse> {
    return apiClient.instance.post(`${AuthApi.BASE_URL}/refresh`);
  }
}

export class DataApi {
  private static BASE_URL = "/query";
  
  public static async getBySourceIP(
    config: IBySourceIP,
  ): Promise<IBySourceIPResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/source-ip`, {
      params: config,
    });
  }

  public static async getByProtocol(
    config: IByProtocol,
  ): Promise<IByProtocolResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/protocol`, {
      params: config,
    });
  }

  public static async getByTimeRange(
    config: IByTimeRange,
  ): Promise<IByTimeRangeResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/time`, {
      params: config,
    });
  }

  public static async getByDestinationPort(
    config: IByDestinationPort,
  ): Promise<IByDestinationPortResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/port`, {
      params: config,
    });
  }

  public static async getBySourceRegion(
    config: IBySourceRegion,
  ): Promise<IBySourceRegionResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/region`, {
      params: config,
    });
  }

  public static async getTimeSeries(
    config: ITimeSeries,
  ): Promise<ITimeSeriesResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/time-series`, {
      params: config,
    });
  }

  public static async getTrafficSummary(
    config: ITrafficSummary,
  ): Promise<ITrafficSummaryResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/traffic-summary`, {
      params: config,
    });
  }

  public static async getProtocolDistribution(
    config: IProtocolDistribution,
  ): Promise<IProtocolDistributionResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/protocol-distribution`, {
      params: config,
    });
  }

  public static async getProtocolAnalysis(
    config: IProtocolAnalysis,
  ): Promise<IProtocolAnalysisResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/protocol-analysis`, {
      params: config,
    });
  }

  public static async getTopSourceIPs(
    config: IByTopSourceIps,
  ): Promise<IByTopSourceIpsResponse> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/top-source-ips`, {
      params: config,
    });
  }
}
