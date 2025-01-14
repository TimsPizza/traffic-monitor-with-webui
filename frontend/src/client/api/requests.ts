import axios from "axios";
import { ENV_CONFIG } from "../config";

export const AXIOS_INSTANCE = axios.create({
  baseURL: ENV_CONFIG.API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});
