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
