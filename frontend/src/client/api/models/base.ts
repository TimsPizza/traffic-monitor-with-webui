export class ApiError extends Error {
  code: number;
  details?: any;

  constructor(message: string, code: number = 500, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
  }

  static fromError(error: unknown): ApiError {
    if (error instanceof ApiError) {
      return error;
    }
    
    if (error instanceof Error) {
      return new ApiError(error.message);
    }

    return new ApiError('Unknown error occurred');
  }
}
export interface ITimeRange {
  start: number;
  end: number;
}
// for query params only, reponse uses IPaginatedResponse<T>
export interface IPagination {
  page: number;
  page_size: number;
}

export interface IRegion {
  region: string;
}