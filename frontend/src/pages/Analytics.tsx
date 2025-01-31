import { useState, useCallback } from "react";
import { TQueryParams, TQueryType } from "../client/types";
import Tables from "../components/Tables";
import FilterChip from "../components/FilterChip";
import { useAnalyticsQuery } from "../hooks/useAnalyticsQuery";
import Dropdown from "../components/Dropdown";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { date2Unix, unix2Date } from "../utils/timetools";

const dropdownOptions: Array<Record<string, TQueryType>> = [
  { TimeRange: "byTimeRange" },
  { Protocol: "byProtocol" },
  { SourceIP: "bySourceIP" },
];

interface IFilter {
  key: string;
  value: string;
}

const Analytics = () => {
  const [queryType, setQueryType] = useState<TQueryType>("byTimeRange");
  const [filters, setFilters] = useState<IFilter[]>([]);
  const [startTime, setStartTime] = useState<number>(
    new Date().getTime() / 1e3,
  );
  const [endTime, setEndTime] = useState<number>(
    new Date().getTime() / 1e3 - 86400,
  );
  const [queryParams, setQueryParams] = useState<TQueryParams>({
    startTime: startTime,
    endTime: endTime,
    protocol: "",
    ipAddress: "",
    page: 1,
    pageSize: 50,
  });

  const handleAddFilter = useCallback(
    (filter: IFilter) => {
      setFilters((prev) => [...prev, filter]);
      setQueryParams((prev) => ({
        ...prev,
        [filter.key]: filter.value,
        startTime: Math.floor(startTime.getTime() / 1000),
        endTime: Math.floor(endTime.getTime() / 1000),
      }));
    },
    [startTime, endTime],
  );

  const handleRemoveFilter = useCallback((index: number) => {
    setFilters((prev) => {
      const newFilters = [...prev];
      const removed = newFilters.splice(index, 1);
      return newFilters;
    });
  }, []);
  const handleQueryTypeSelect = (selected: string) => {
    let target = dropdownOptions.find((option) => option[selected])![selected];
    console.log("target", target);
    setQueryType(target);
  };
  const handleQueryPageSizeSelect = (selected: string) => {
    let pageSizeNumber = parseInt(selected);
    setQueryParams((prev) => {
      return Object.assign({}, prev, { pageSize: pageSizeNumber });
    });
  };

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
    // disable refetch by default
    refetchInterval: false,
  });

  const handleQuery = (type: TQueryType, params: any) => {
    setQueryType(type);
    setQueryParams(() => Object.assign({}, params));
    console.log("setQueryParams", queryParams);
  };

  return (
    <div className="p-4">
      <div className="mb-4 flex flex-col gap-4">
        {/* Active Filters */}
        <div className="flex flex-wrap gap-2">
          {filters.map((filter, index) => (
            <FilterChip
              key={index}
              filter={filter}
              onRemove={() => handleRemoveFilter(index)}
            />
          ))}
        </div>

        {/* Query Controls */}
        <div className="flex h-10 gap-4">
          <Dropdown
            options={dropdownOptions.map((obj) => Object.keys(obj)[0])}
            label="Query By"
            handleSelect={handleQueryTypeSelect}
          />
          {/* Time Range Picker */}
          <div
            id="selectors-wrapper"
            className="flex h-full items-center gap-4"
          >
            <div
              id="start-date-picker-selector-wrapper"
              className="flex items-center gap-2"
            >
              <span>From:</span>
              <DatePicker
                selected={unix2Date(startTime)}
                onChange={(date: Date) => setStartTime(date2Unix(date))}
                showTimeSelect
                timeFormat="HH:mm"
                timeIntervals={15}
                dateFormat="MMMM d, yyyy h:mm aa"
                className="z-10 rounded border p-2"
              />
            </div>
            <div
              id="end-date-picker-selector-wrapper"
              className="flex items-center gap-2"
            >
              <span>To:</span>
              <DatePicker
                selected={unix2Date(endTime)}
                onChange={(date: Date) => setEndTime(date)}
                showTimeSelect
                timeFormat="HH:mm"
                timeIntervals={15}
                dateFormat="MMMM d, yyyy h:mm aa"
                className="z-10 rounded border p-2"
              />
            </div>
            <div
              id="page-size-selector-wrapper"
              className="flex h-full items-center justify-center gap-2"
            >
              <span>Page Size:</span>
              <Dropdown
                options={["10", "20", "30", "40", "50"]}
                label="Page Size"
                handleSelect={handleQueryPageSizeSelect}
              />
            </div>
            <button
              className="rounded bg-blue-500 p-2 text-white"
              onClick={() => handleQuery(queryType, queryParams)}
            >
              Query
            </button>
          </div>
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
              setQueryParams((prev) => ({
                ...prev,
                page: (prev.page || 1) + 1,
              }))
            }
            fetchPreviousPage={() =>
              setQueryParams((prev) => ({
                ...prev,
                page: (prev.page || 1) - 1,
              }))
            }
            onFilterAdd={handleAddFilter}
          />
        )}
      </div>
    </div>
  );
};

export default Analytics;
