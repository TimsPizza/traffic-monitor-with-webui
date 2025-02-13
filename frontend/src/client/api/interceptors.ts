import { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from "axios";
import { IApiError } from "./models/base";

export class RequestInterceptors {
  public static addAuthHeader = (
    config: InternalAxiosRequestConfig,
  ): InternalAxiosRequestConfig => {
    const accessToken = localStorage.getItem("access_token");
    config.headers.Authorization = `Bearer ${accessToken}`;
    return config;
  };
}

export class ResponseInterceptors {
  public static handleAuthError = async (
    response: AxiosResponse,
  ): Promise<AxiosResponse> => {
    if (response.status === 401) {
      console.error("Unauthorized request, trying to refresh token...");
      await ResponseInterceptors.handleRefreshToken();
    }
    return response;
  };

  private static handleRefreshToken = async (): Promise<void> => {
    // TODO: Implement refresh token logic
    console.error("Refresh token logic not implemented");
  };

  public static handleHttpError = (error: AxiosError): Promise<IApiError> => {
    if (error.response) {
      return Promise.reject({
        code: error.response.status,
        message: error.response.data,
      });
    }
    return Promise.reject(error);
  };
}
