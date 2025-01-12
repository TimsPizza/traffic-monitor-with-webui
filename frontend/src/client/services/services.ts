import axios from "axios";
import { ENV_CONFIG } from "../config";
import {
  TAuthResponse,
  TLoginForm,
  TSignUpForm,
  TSignUpResponse,
  TUser,
} from "../models/models";
import { TQueryParams, TQueryType } from "../types";

const API_BASE = ENV_CONFIG.API_BASE_URL;

export class AuthService {
  public static signUp = async (
    formData: TSignUpForm,
  ): Promise<TSignUpResponse> => {
    const response = await axios.post(
      `${API_BASE}/auth/register`,
      {
        username: formData.username,
        password: formData.password,
      },
    );
    return response.data;
  };

  public static login = async (
    formData: TLoginForm,
  ): Promise<TAuthResponse> => {
    const response = await axios.post<TAuthResponse>(
      `${API_BASE}/auth/token`,
      {
        username: formData.username,
        password: formData.password,
      },
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      },
    );
    return response.data;
  };

  public static logout = async (): Promise<void> => {
    await axios.post(`${API_BASE}/auth/logout`);
  };

  public static refreshToken = async (): Promise<TAuthResponse> => {
    const response = await axios.post<TAuthResponse>(
      `${API_BASE}/auth/refresh`,
    );
    return response.data;
  };
  public static readUser = async (): Promise<TUser> => {
    const response = await axios.post<TUser>(`${API_BASE}/user`, {
      Headers:{
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      }
    });
    return response.data;
  };
}
 
export class QueryService {
  public static queryPackets = async (
    type: TQueryType,
    params: TQueryParams,
  ) => {
    let url = `/query/${type}`;
    let token = localStorage.getItem("access_token") || "";
    const queryParams = new URLSearchParams({
      page: params.page?.toString() || "1",
      pageSize: params.pageSize?.toString() || "50",
    });

    switch (type) {
      case "time":
        if (params.startTime && params.endTime) {
          queryParams.set("start_time", params.startTime.toString());
          queryParams.set("end_time", params.endTime.toString());
        }
        break;
      case "protocol":
        if (params.protocol) {
          queryParams.set("protocol", params.protocol);
        }
        break;
      case "source-ip":
        if (params.ipAddress) {
          queryParams.set("ip_address", params.ipAddress);
        }
        break;
    }

    const response = await axios.get(`${url}?${queryParams.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  }
}
