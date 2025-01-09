interface EnvConfig {
  API_BASE_URL: string;
  APP_NAME: string;
}

export const ENV_CONFIG: EnvConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  APP_NAME: import.meta.env.VITE_APP_NAME || "Vite App",
};

export type { EnvConfig };
