import React, { useEffect, useState } from "react";
import {
  FiFilter,
  FiPlus,
  FiEdit2,
  FiTrash2,
  FiSave,
  FiX,
} from "react-icons/fi";
import { configService } from "../../client/services/config";
import type { ICaptureFilter } from "../../client/api/models/request";
import type { TFilterAllResponse } from "../../client/api/models/response";
import { useQuery } from "react-query";

const FilterRulesCard: React.FC = () => {
  const [filters, setFilters] = useState<ICaptureFilter[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editingFilter, setEditingFilter] = useState<ICaptureFilter | null>(
    null,
  );
  const [newFilter, setNewFilter] = useState<ICaptureFilter | null>(null);
  const query = useQuery({
    queryKey: "filters",
    queryFn: configService.getFilters,
    onSuccess: (data: TFilterAllResponse) => {
      setFilters(data);
    },
    onError: (error) => {
      console.error("Failed to load filters:", error);
      setError("Failed to load filters");
    },
    refetchInterval: false,
    retry: 3,
  });
  useEffect(() => {}, []);

  const handleAddFilter = () => {
    setNewFilter({
      src_ip: null,
      dst_ip: null,
      src_port: null,
      dst_port: null,
      protocol: null,
      operation: "Include",
      direction: "Inbound",
    });
  };

  const handleSaveFilters = async (newFilters: ICaptureFilter[]) => {
    try {
      setError(null);
      await configService.setFilters(newFilters);
      setFilters(newFilters);
      setEditingFilter(null);
      setNewFilter(null);
    } catch (error) {
      console.error("Failed to save filters:", error);
      setError("Failed to save filters");
    }
  };

  const FilterEditor: React.FC<{
    filter: ICaptureFilter;
    onSave: (filter: ICaptureFilter) => void;
    onCancel: () => void;
  }> = ({ filter, onSave, onCancel }) => (
    <div className="space-y-4 rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Source IP
          </label>
          <input
            type="text"
            className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
            value={filter.src_ip || ""}
            onChange={(e) =>
              onSave({ ...filter, src_ip: e.target.value || null })
            }
            placeholder="e.g. 192.168.1.1"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Destination IP
          </label>
          <input
            type="text"
            className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
            value={filter.dst_ip || ""}
            onChange={(e) =>
              onSave({ ...filter, dst_ip: e.target.value || null })
            }
            placeholder="e.g. 192.168.1.2"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium dark:text-gray-300">
            Source Ports
          </label>
          <input
            type="text"
            className="w-full rounded-lg border border-gray-200 px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
            value={filter.src_port?.join(", ") || ""}
            onChange={(e) => {
              const ports = e.target.value
                .split(",")
                .map((p) => parseInt(p.trim()))
                .filter((p) => !isNaN(p));
              onSave({ ...filter, src_port: ports.length ? ports : null });
            }}
            placeholder="e.g. 80, 443"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium dark:bg-gray-700 dark:text-gray-300">
            Destination Ports
          </label>
          <input
            type="text"
            className="w-full rounded-lg border border-gray-200 px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
            value={filter.dst_port?.join(", ") || ""}
            onChange={(e) => {
              const ports = e.target.value
                .split(",")
                .map((p) => parseInt(p.trim()))
                .filter((p) => !isNaN(p));
              onSave({ ...filter, dst_port: ports.length ? ports : null });
            }}
            placeholder="e.g. 80, 443"
          />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium dark:bg-gray-700 dark:text-gray-300">
            Protocol
          </label>
          <select
            className="w-full rounded-lg border border-gray-200 px-3 py-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300"
            value={filter.protocol || ""}
            onChange={(e) =>
              onSave({
                ...filter,
                protocol: (e.target.value ||
                  null) as ICaptureFilter["protocol"],
              })
            }
          >
            <option value="">Any</option>
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
            <option value="icmp">ICMP</option>
            <option value="all">ALL</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Operation
          </label>
          <select
            className="w-full rounded-lg border border-gray-200 px-3 py-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300"
            value={filter.operation}
            onChange={(e) =>
              onSave({
                ...filter,
                operation: e.target.value as "Include" | "Exclude",
              })
            }
          >
            <option value="Include">Include</option>
            <option value="Exclude">Exclude</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Direction
          </label>
          <select
            className="w-full rounded-lg border border-gray-200 px-3 py-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300"
            value={filter.direction}
            onChange={(e) =>
              onSave({
                ...filter,
                direction: e.target.value as "Inbound" | "Outbound",
              })
            }
          >
            <option value="Inbound">Inbound</option>
            <option value="Outbound">Outbound</option>
          </select>
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <button
          onClick={() => {
            const updatedFilters = editingFilter
              ? filters.map((f) =>
                  JSON.stringify(f) === JSON.stringify(editingFilter)
                    ? filter
                    : f,
                )
              : [...filters, filter];
            handleSaveFilters(updatedFilters);
          }}
          className="rounded-lg bg-blue-500 px-4 py-2 text-gray-50 hover:bg-blue-600"
        >
          <FiSave className="h-5 w-5" />
        </button>
        <button
          onClick={onCancel}
          className="rounded-lg bg-gray-500 px-4 py-2 text-gray-50 hover:bg-gray-600"
        >
          <FiX className="h-5 w-5" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="rounded-xl bg-gray-50 p-6 shadow-lg transition-all duration-300 hover:shadow-xl dark:bg-gray-800">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-green-500 to-green-600">
            <FiFilter className="h-6 w-6 text-gray-50" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-50">
            Capture Filters
          </h3>
        </div>
        <button
          onClick={handleAddFilter}
          className="flex items-center gap-2 rounded-lg bg-green-500 px-4 py-2 text-gray-50 hover:bg-green-600"
        >
          <FiPlus className="h-5 w-5" />
          Add Filter
        </button>
      </div>

      {query.isLoading ? (
        <div className="animate-pulse space-y-3">
          {[1, 2].map((i) => (
            <div
              key={i}
              className="h-32 w-full rounded-lg bg-gray-200 dark:bg-gray-700"
            />
          ))}
        </div>
      ) : query.isError ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-600 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {newFilter && (
            <FilterEditor
              filter={newFilter}
              onSave={(filter) => handleSaveFilters([...filters, filter])}
              onCancel={() => setNewFilter(null)}
            />
          )}
          {filters.map((filter, index) =>
            editingFilter &&
            JSON.stringify(filter) === JSON.stringify(editingFilter) ? (
              <FilterEditor
                key={index}
                filter={editingFilter}
                onSave={(updatedFilter) => {
                  const newFilters = [...filters];
                  newFilters[index] = updatedFilter;
                  handleSaveFilters(newFilters);
                }}
                onCancel={() => setEditingFilter(null)}
              />
            ) : (
              <div
                key={index}
                className="rounded-lg bg-gray-50 p-4 dark:bg-gray-700"
              >
                <div className="flex items-center justify-between">
                  <div className="grid grid-cols-4 gap-4">
                    <div>
                      <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        Source:
                      </span>
                      <span className="ml-2 text-gray-900 dark:text-gray-50">
                        {filter.src_ip || "Any IP"}
                        {filter.src_port
                          ? ` (Ports: ${filter.src_port.join(", ")})`
                          : ""}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        Destination:
                      </span>
                      <span className="ml-2 text-gray-900 dark:text-gray-50">
                        {filter.dst_ip || "Any IP"}
                        {filter.dst_port
                          ? ` (Ports: ${filter.dst_port.join(", ")})`
                          : ""}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        Protocol:
                      </span>
                      <span className="ml-2 text-gray-900 dark:text-gray-300">
                        {filter.protocol || "Any"}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        Rule:
                      </span>
                      <span className="ml-2 text-gray-900 dark:text-gray-300">
                        {filter.operation} {filter.direction} traffic
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setEditingFilter(filter)}
                      className="rounded-lg p-2 text-gray-500 hover:bg-gray-200 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-600 dark:hover:text-gray-200"
                    >
                      <FiEdit2 className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() =>
                        handleSaveFilters(filters.filter((f) => f !== filter))
                      }
                      className="rounded-lg p-2 text-red-500 hover:bg-red-100 hover:text-red-700 dark:hover:bg-red-900"
                    >
                      <FiTrash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            ),
          )}
        </div>
      )}
    </div>
  );
};

export default FilterRulesCard;
