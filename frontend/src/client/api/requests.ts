import axios, { AxiosInstance } from "axios";
import { ENV_CONFIG } from "../config";

type Resolver<T> = (options: TApiRequestOptions<T>) => Promise<T>;
export type TApiResult<TData = any> = {
  readonly body: TData;
  readonly ok: boolean;
  readonly status: number;
  readonly statusText: string;
  readonly url: string;
};

export type TApiRequestOptions<T = unknown> = {
  readonly body?: any;
  readonly cookies?: Record<string, unknown>;
  readonly errors?: Record<number | string, string>;
  readonly formData?: Record<string, unknown> | any[] | Blob | File;
  readonly headers?: Record<string, unknown>;
  readonly mediaType?: string;
  readonly method:
    | "DELETE"
    | "GET"
    | "HEAD"
    | "OPTIONS"
    | "PATCH"
    | "POST"
    | "PUT";
  readonly path?: Record<string, unknown>;
  readonly query?: Record<string, unknown>;
  readonly responseHeader?: string;
  readonly responseTransformer?: (data: unknown) => Promise<T>;
  readonly url: string;
};

export class TApiError extends Error {
  public readonly url: string;
  public readonly status: number;
  public readonly statusText: string;
  public readonly body: unknown;
  public readonly request: TApiRequestOptions;

  constructor(
    request: TApiRequestOptions,
    response: TApiResult,
    message: string,
  ) {
    super(message);

    this.name = "ApiError";
    this.url = response.url;
    this.status = response.status;
    this.statusText = response.statusText;
    this.body = response.body;
    this.request = request;
  }
}
