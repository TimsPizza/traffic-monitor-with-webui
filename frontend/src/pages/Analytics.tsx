import { useCallback, useState } from "react";
import DatePicker from "react-datepicker";
import { TQueryParams, TQueryType } from "../client/types";
import Dropdown from "../components/Dropdown";
import FilterChip from "../components/FilterChip";
import Tables from "../components/Tables";
import { useAnalyticsQuery } from "../hooks/useAnalyticsQuery";
import useToast from "../hooks/useToast";
import { date2Unix, unix2Date } from "../utils/timetools";
import { findArrItemByKey } from "../utils/tools";

interface IDropDownOption {
  // key: display text, value: query type
  key: string;
  value: TQueryType;
}

interface IFilter {
  key: string;
  value: string;
}

const dropdownOptions: Array<IDropDownOption> = [
  {key: "TimeRange", value: "byTimeRange"},
  {key: "Protocol", value: "byProtocol"}, 
  {key: "SourceIP", value: "bySourceIP"},
];

const Analytics = () => {
  const toast = useToast({
    position: "top-right",
  });
  const [queryType, setQueryType] = useState<TQueryType>("byTimeRange");
  const [filters, setFilters] = useState<IFilter[]>([]);
  const [queryParams, setQueryParams_] = useState<TQueryParams>({
    start: Date.now() / 1e3 - 86400,
    end: Date.now() / 1e3,
    protocol: "",
    ip_address: "",
    page: 1,
    page_size: 50,
    port: -1,
    region: "",
  });

  const setQueryParams = (key: string, value: any) => {
    if (!(key in queryParams)) {
      return;
    }
    setQueryParams_((prev) => {
      return Object.assign({}, prev, { [key]: value });
    });
  };

  const {
    data,
    error,
    isLoading,
    refetch,
    hasNextPage,
    hasPreviousPage,
    currentPage,
    totalItems,
    totalPages,
  } = useAnalyticsQuery({
    queryType: queryType,
    params: queryParams,
  });

  const handleAddFilter = useCallback((filter: IFilter) => {
    setFilters((prev) => [...prev, filter]);
    setQueryParams(filter.key, filter.value);
  }, []);

  const handleRemoveFilter = useCallback((index: number) => {
    setFilters((prev) => {
      const newFilters = [...prev];
      const removed = newFilters.splice(index, 1);
      return newFilters;
    });
  }, []);

  const handleQueryTypeSelect = (selected: string) => {
    // 'selected' is the value of the selected dropdown option
    let target = dropdownOptions.find((item) => item.key === selected)?.value ?? "byTimeRange";
    console.log("selected", selected, "target", target);
    setQueryType(target);
  };

  const handleQueryPageSizeSelect = (selected: string) => {
    let pageSizeNumber = parseInt(selected);
    setQueryParams("page_size", pageSizeNumber.toString());
  };

  const handleStartTimeSelect = (date: Date | null) => {
    if (date && queryParams.end) {
      if (date2Unix(date) >= queryParams.end) {
        toast.error("Start time must be before end time");
        return;
      } else {
        setQueryParams("start", date2Unix(date));
      }
    }
  };

  const handleEndTimeSelect = (date: Date | null) => {
    if (date && queryParams.start) {
      if (date2Unix(date) <= queryParams.start) {
        toast.error("End time must be after start time");
        return;
      } else {
        setQueryParams("end", date2Unix(date));
      }
    }
  };

  const handleQuery = () => {
    refetch();
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

        <div className="flex h-10 gap-4">
          <Dropdown
            options={dropdownOptions.map((obj) => obj.key)}
            label="Query By"
            minW="128px"
            selected={
              dropdownOptions.find((item) => item.value === queryType)?.key ?? "Query Type"
            }
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
                selected={unix2Date(queryParams.start ?? 0)}
                onChange={(date: Date | null) =>
                  date && handleStartTimeSelect(date)
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
                selected={unix2Date(queryParams.end ?? 0)}
                onChange={(date: Date | null) =>
                  date && handleEndTimeSelect(date)
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
                selected={queryParams.page_size?.toString() || "undefined"}
                handleSelect={handleQueryPageSizeSelect}
              />
            </div>
            <button
              className="rounded bg-blue-500 p-2 text-white"
              onClick={handleQuery}
            >
              Query
            </button>
          </div>
        </div>

        {isLoading && <div>Loading...</div>}
        {error && <div>Error fetching data</div>}
        {data && (
          <Tables
            data={data as any}
            currentPage={currentPage ?? 1}
            maxPage={totalPages}
            pageSize={data.length}
            hasPreviousPage={hasPreviousPage ?? false}
            hasNextPage={hasNextPage ?? false}
            fetchNextPage={() => {
              setQueryParams("page", queryParams.page! + 1);
            }}
            fetchPreviousPage={() => {
              setQueryParams("page", queryParams.page! - 1);
            }}
            onFilterAdd={handleAddFilter}
          />
        )}
      </div>
    </div>
  );
};

export default Analytics;
