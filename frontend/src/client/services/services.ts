import axios from "axios";
import { ENV_CONFIG } from "../config";
export interface RegisterParams {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

const API_BASE = ENV_CONFIG.API_BASE_URL;

class AuthService {
  public static register = async (
    username: string,
    password: string,
  ): Promise<AuthResponse> => {
    const response = await axios.post<AuthResponse>(
      `${API_BASE}/auth/register`,
      {
        username,
        password,
      },
    );
    return response.data;
  };

  public static login = async (
    username: string,
    password: string,
  ): Promise<AuthResponse> => {
    const response = await axios.post<AuthResponse>(
      `${API_BASE}/auth/token`,
      {
        username,
        password,
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

  public static refreshToken = async (): Promise<AuthResponse> => {
    const response = await axios.post<AuthResponse>(`${API_BASE}/auth/refresh`);
    return response.data;
  };
}
