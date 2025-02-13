import axios, { AxiosInstance } from "axios";
import { RequestInterceptors, ResponseInterceptors } from "./interceptors";

class ApiClient {
  public readonly instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 10000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Setup interceptors
    // Request interceptors
    this.instance.interceptors.request.use(RequestInterceptors.addAuthHeader);

    // Response interceptors
    this.instance.interceptors.response.use(
      ResponseInterceptors.handleAuthError,
      null,
    );
    this.instance.interceptors.response.use(
      null,
      ResponseInterceptors.handleHttpError,
    );
  }
}

export const apiClient = new ApiClient();
