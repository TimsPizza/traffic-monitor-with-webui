import { useState } from "react";
import Tables from "../components/Tables";
import { IBySourceIPResponse, TQueryParams, TQueryType } from "../client/types";
import { useAnalyticsQuery } from "../hooks/useAnalyticsQuery";
import { date2Unix } from "../utils/timetools";
import { Prev } from "react-bootstrap/esm/PageItem";
import { IBySourceIP } from "../client/api/models/request";

const Analytics = () => {
  const [queryType, setQueryType] = useState<"time" | "protocol" | "source-ip">(
    "time",
  );
  const [queryParams, setQueryParams] = useState<TQueryParams>({
    startTime: 86400,
    endTime: Date.now() / 1e3,
    protocol: "",
    ipAddress: "",
    page: 1,
    pageSize: 20,
  });

  const { data, error, isLoading, hasNextPage, hasPreviousPage } =
    useAnalyticsQuery<IBySourceIP, IBySourceIPResponse>(
      "bySourceIP",
      {
        ip_address: queryParams.ipAddress || "",
        start: queryParams.startTime || 0,
        end: queryParams.endTime || new Date().getTime() / 1e3,
        page: queryParams.page || 1,
        page_size: queryParams.pageSize || 20,
      },
      5000,
    );

  const handleQuery = (type: TQueryType, params: any) => {
    setQueryType(type);
    setQueryParams((prev) => ({ ...prev, ...params }));
    console.log("setQueryParams", queryParams);
  };

  return (
    <div className="p-4">
      <div className="mb-4 flex gap-4">
        <button
          onClick={() =>
            handleQuery("time", { startTime: 86400, endTime: Date.now() / 1e3 })
          }
          className="rounded bg-blue-500 px-4 py-2 text-white"
        >
          Query by Time
        </button>
        <button
          onClick={() =>
            handleQuery("protocol", {
              protocol: "HTTPS",
              startTime: 86400,
              endTime: Date.now() / 1e3,
            })
          }
          className="rounded bg-blue-500 px-4 py-2 text-white"
        >
          Query by Protocol
        </button>
        <button
          onClick={() =>
            handleQuery("source-ip", {
              ipAddress: "192.168.1.1",
              startTime: 86400,
              endTime: Date.now() / 1e3,
            })
          }
          className="rounded bg-blue-500 px-4 py-2 text-white"
        >
          Query by Source IP
        </button>
      </div>

      {isLoading && <div>Loading...</div>}
      {error && <div>Error fetching data</div>}
      {data && (
        <Tables
          data={data}
          hasPreviousPage={hasPreviousPage}
          hasNextPage={hasNextPage}
          // fetchNextPage={setQueryParams((prev) => ({ ...prev, page: prev.page + 1 }))}
          // fetchPreviousPage={fetchPreviousPage}
        />
      )}
    </div>
  );
};

export default Analytics;
