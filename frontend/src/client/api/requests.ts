import {
  IAccessRecord,
  ICaptureFilter,
  TAuthResponse,
  TLoginForm,
  TSignUpForm,
} from "../models/models";
import { apiClient } from "./apiClient";

export class AuthApi {
  public static login(data: TLoginForm): Promise<TAuthResponse> {
    return apiClient.instance.post("/auth/login", data);
  }

  public static signup(data: TSignUpForm): Promise<TAuthResponse> {
    return apiClient.instance.post("/auth/signup", data);
  }

  public static logout(): Promise<void> {
    return apiClient.instance.post("/auth/logout");
  }

  public static refreshToken(): Promise<TAuthResponse> {
    return apiClient.instance.post("/auth/refresh");
  }
}

export class DataApi {
  public static getAccessRecords(
    filter: ICaptureFilter,
  ): Promise<IAccessRecord[]> {
    return apiClient.instance.post("/data/access-records", filter);
  }
}
