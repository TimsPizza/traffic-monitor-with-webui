import axios, { AxiosInstance } from 'axios';
import { RequestInterceptors, ResponseInterceptors } from './interceptors';

class ApiClient {
  public readonly instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Setup interceptors
    this.instance.interceptors.request.use(
      RequestInterceptors.addAuthHeader
    );
    this.instance.interceptors.response.use(
      ResponseInterceptors.handleAuthError
    );
  }
}

export const apiClient = new ApiClient();
