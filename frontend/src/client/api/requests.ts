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
  TLoginForm,
  TSignUpForm,
} from "../api/models/request";
import {
  IByDestinationPortResponse,
  IByProtocolResponse,
  IBySourceIPResponse,
  IBySourceRegionResponse,
  IByTimeRangeResponse,
  IByTopSourceIpsResponse,
  IPaginatedResponse,
  IProtocolDistributionResponse,
  ITimeSeriesResponse,
  ITrafficSummaryResponse,
  TAuthResponse,
} from "../api/models/response";
import { apiClient } from "./apiClient";

const cleanQueryParams = (query: Object) => {
  return Object.entries(query).reduce((acc, [key, value]) => {
    if (value === "") return acc;
    return { ...acc, [key]: value };
  }, {});
};

export class AuthApi {
  private static BASE_URL = "/auth";
  public static login(data: TLoginForm): Promise<TAuthResponse> {
    return apiClient.instance.post(
      `${AuthApi.BASE_URL}/login`,
      cleanQueryParams(data),
    );
  }

  public static signup(data: TSignUpForm): Promise<TAuthResponse> {
    return apiClient.instance.post(
      `${AuthApi.BASE_URL}/signup`,
      cleanQueryParams(data),
    );
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
  ): Promise<IPaginatedResponse<IBySourceIPResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/source-ip`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getByProtocol(
    config: IByProtocol,
  ): Promise<IPaginatedResponse<IByProtocolResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/protocol`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getByTimeRange(
    config: IByTimeRange,
  ): Promise<IPaginatedResponse<IByTimeRangeResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/time`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getByDestinationPort(
    config: IByDestinationPort,
  ): Promise<IPaginatedResponse<IByDestinationPortResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/port`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getBySourceRegion(
    config: IBySourceRegion,
  ): Promise<IPaginatedResponse<IBySourceRegionResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/region`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getTimeSeries(
    config: ITimeSeries,
  ): Promise<IPaginatedResponse<ITimeSeriesResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/time-series`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getTrafficSummary(
    config: ITrafficSummary,
  ): Promise<IPaginatedResponse<ITrafficSummaryResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/traffic-summary`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getProtocolDistribution(
    config: IProtocolDistribution,
  ): Promise<IPaginatedResponse<IProtocolDistributionResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/protocol-distribution`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getProtocolAnalysis(
    config: IProtocolAnalysis,
  ): Promise<IPaginatedResponse<IProtocolAnalysisResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/protocol-analysis`, {
      params: cleanQueryParams(config),
    });
  }

  public static async getTopSourceIPs(
    config: IByTopSourceIps,
  ): Promise<IPaginatedResponse<IByTopSourceIpsResponse>> {
    return apiClient.instance.get(`${DataApi.BASE_URL}/top-source-ips`, {
      params: cleanQueryParams(config),
    });
  }
}
