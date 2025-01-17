import { InternalAxiosRequestConfig, AxiosResponse } from 'axios';

export class RequestInterceptors {
  public static addAuthHeader = (
    config: InternalAxiosRequestConfig
  ): InternalAxiosRequestConfig => {
    // TODO: Add auth header logic
    return config;
  };
}

export class ResponseInterceptors {
  public static handleAuthError = (
    response: AxiosResponse
  ): AxiosResponse => {
    // TODO: Add error handling logic
    return response;
  };
}
