import { InternalAxiosRequestConfig, AxiosResponse } from "axios";

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
  public static handleAuthError = (response: AxiosResponse): AxiosResponse => {
    // TODO: Add error handling logic
    // TODO: Add refresh token implementation, both frontend and backend
    if (response.status === 401) {
      console.error("Unauthorized request");
    }
    return response;
  };
  private static handleRefreshToken = async (): Promise<void> => {
    // TODO: Implement refresh token logic
    console.error("Refresh token logic not implemented");
  };
}
