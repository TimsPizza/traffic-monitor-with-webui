import { useState } from "react";
import { TQueryParams, TQueryType } from "../client/types";
import Tables from "../components/Tables";
import { useAnalyticsQuery } from "../hooks/useAnalyticsQuery";
import Dropdown from "../components/Dropdown";

const dropdownOptions: Array<Record<string, TQueryType>> = [
  { TimeRange: "byTimeRange" },
  { Protocol: "byProtocol" },
  { SourceIP: "bySourceIP" },
];

const Analytics = () => {
  const [queryType, setQueryType] = useState<TQueryType>("byTimeRange");
  const handleDropdownSelect = (selected: string) => {
    let target = dropdownOptions.find((option) => option[selected])![selected];
    console.log("target", target);
    setQueryType(target);
  };
  const [queryParams, setQueryParams] = useState<TQueryParams>({
    startTime: Date.now() / 1e3 - 86400 - 300,
    endTime: Date.now() / 1e3 - 86400,
    protocol: "",
    ipAddress: "",
    page: 1,
    pageSize: 50,
  });

  const {
    data,
    error,
    isLoading,
    maxPage,
    currentPage,
    hasNextPage,
    hasPreviousPage,
  } = useAnalyticsQuery(queryType, {
    ip_address: queryParams.ipAddress || "",
    protocol: queryParams.protocol || "",
    start: queryParams.startTime || 0,
    end: queryParams.endTime || new Date().getTime() / 1e3,
    page: queryParams.page || 1,
    page_size: queryParams.pageSize || 20,
  });

  const handleQuery = (type: TQueryType, params: any) => {
    setQueryType(type);
    setQueryParams((prev) => ({ ...prev, ...params }));
    console.log("setQueryParams", queryParams);
  };

  return (
    <div className="p-4">
      <div className="mb-4 flex gap-4">
        <Dropdown
          options={dropdownOptions.map(obj => Object.keys(obj)[0])}
          label="Query By"
          handleSelect={handleDropdownSelect}
        />
        <button
          onClick={() =>
            handleQuery("byTimeRange", {
              startTime: Date.now() / 1e3 - 86400 - 7200,
              endTime: Date.now() / 1e3 - 86400,
            })
          }
          className="rounded bg-blue-500 px-4 py-2 text-white"
        >
          Query by Time
        </button>
        <button
          onClick={() =>
            handleQuery("byProtocol", {
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
            handleQuery("bySourceIP", {
              ipAddress: "142.66.76.33",
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
          currentPage={currentPage}
          maxPage={maxPage}
          hasPreviousPage={hasPreviousPage}
          hasNextPage={hasNextPage}
          fetchNextPage={() =>
            setQueryParams((prev) => ({ ...prev, page: prev.page + 1 }))
          }
          fetchPreviousPage={() =>
            setQueryParams((prev) => ({ ...prev, page: prev.page - 1 }))
          }
        />
      )}
    </div>
  );
};

export default Analytics;
