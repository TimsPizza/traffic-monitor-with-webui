import { useState, useCallback, useRef } from "react";
import { TQueryParams, TQueryType } from "../client/types";
import Tables from "../components/Tables";
import FilterChip from "../components/FilterChip";
import { useAnalyticsQuery } from "../hooks/useAnalyticsQuery";
import Dropdown from "../components/Dropdown";
import DatePicker from "react-datepicker";
import {
  date2Unix,
  dateString2Unix,
  unix2Date,
  unix2DateString,
} from "../utils/timetools";
import useToast from "../hooks/useToast";
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
  const toast = useToast();
  const [queryType, setQueryType] = useState<TQueryType>("byTimeRange");
  const [filters, setFilters] = useState<IFilter[]>([]);
  const [startTime, setStartTime_] = useState<number>(
    new Date().getTime() / 1e3,
  );
  const [endTime, setEndTime_] = useState<number>(
    // set end time to 24 hours ago as init value
    new Date().getTime() / 1e3 - 86400,
  );
  const queryParams = useRef<TQueryParams>({
    startTime: startTime,
    endTime: endTime,
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
    ip_address: queryParams.current.ipAddress || "",
    protocol: queryParams.current.protocol || "",
    start: queryParams.current.startTime || 0,
    end: queryParams.current.endTime || new Date().getTime() / 1e3,
    page: queryParams.current.page || 1,
    page_size: queryParams.current.pageSize || 20,
    // disable refetch by default
    refetchInterval: false,
  });
  const setStartTime = (date: number) => {
    if (date >= endTime) {
      toast.error("Start time should be earlier than end time!", {
        position: "top-center",
      });
    }
    setStartTime_(date);
  };
  const setEndTime = (date: number) => {
    if (date <= startTime) {
      toast.error("End time should be later than start time!", {
        position: "top-center",
      });
    }
    setEndTime_(date);
  };
  const handleAddFilter = useCallback(
    (filter: IFilter) => {
      setFilters((prev) => [...prev, filter]);
      queryParams.current = Object.assign({}, queryParams.current, filter);
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
    queryParams.current = Object.assign({}, queryParams.current, {
      pageSize: pageSizeNumber,
    });
  };

  const handleQuery = (type: TQueryType, params: any) => {
    setQueryType(type);
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
            minW="128px"
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
                onChange={(date: Date | null) =>
                  date && setStartTime(date2Unix(date))
                }
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
                onChange={(date: Date | null) =>
                  date && setEndTime(date2Unix(date))
                }
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
