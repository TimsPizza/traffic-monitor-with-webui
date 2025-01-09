import axios from 'axios'
import { ENV_CONFIG } from '../config'

const API_BASE = ENV_CONFIG.API_BASE_URL

export interface RegisterParams {
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export const register = async (username: string, password: string): Promise<AuthResponse> => {
  const response = await axios.post<AuthResponse>(`${API_BASE}/auth/register`, {
    username,
    password
  })
  return response.data
}

export const login = async (username: string, password: string): Promise<AuthResponse> => {
  const response = await axios.post<AuthResponse>(`${API_BASE}/auth/token`, {
    username,
    password
  }, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
  return response.data
}

export const logout = async (): Promise<void> => {
  await axios.post(`${API_BASE}/auth/logout`)
}

export const refreshToken = async (): Promise<AuthResponse> => {
  const response = await axios.post<AuthResponse>(`${API_BASE}/auth/refresh`)
  return response.data
}
