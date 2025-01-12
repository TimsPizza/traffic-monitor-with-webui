export interface ICaptureFilter {
  src_ip?: string | null;
  dst_ip?: string | null;
  src_port?: number[];
  dst_port?: number[];
  protocol?: "tcp" | "udp" | "icmp" | "all";
}

export interface IAccessRecord {
  id: number;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  src_region: string;
  dst_port: number;
  protocol: string;
  timestamp: string;
}

export type TLoginForm = {
  username: string;
  password: string;
};

export type TUser = {
  username: string;
};

export type TSignUpForm = {
  username: string;
  password: string;
};

export type TSignUpResponse = {
  username: string;
  password_hash: string;
  created_at: number;
  last_login: number;
  is_active: boolean;
}

export type TAuthResponse = {
  access_token: string;
  token_type: string;
};
