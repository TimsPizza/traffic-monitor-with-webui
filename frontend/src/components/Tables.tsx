import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getSortedRowModel,
  getPaginationRowModel,
} from "@tanstack/react-table";
import { useEffect } from "react";
import { IFullAccessRecordResponse } from "../client/api/models/response";

const columnHelper = createColumnHelper<IFullAccessRecordResponse>();

const columns = [
  columnHelper.accessor("id", {
    header: "ID",
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor("src_ip", {
    header: "Source IP",
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor("region", {
    header: "Region",
    cell: (info) => {
      if (info && info.getValue()) {
        return info.getValue().toUpperCase();
      }
    },
  }),
  columnHelper.accessor("protocol", {
    header: "Protocol",
    cell: (info) => {
      if (info && info.getValue()) {
        return info.getValue().toUpperCase();
      }
    },
  }),
  columnHelper.accessor("dst_port", {
    header: "Destination Port",
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor("timestamp", {
    header: "Time",
    cell: (info) => info.getValue(),
  }),
];

// type TAcceptableTableData = IRe

interface TableProps {
  data: IFullAccessRecordResponse[];
  currentPage: number;
  maxPage: number;
  hasPreviousPage: boolean;
  hasNextPage: boolean;
  fetchNextPage: () => void;
  fetchPreviousPage: () => void;
}

const Tables: React.FC<TableProps> = ({
  data,
  currentPage,
  maxPage,
  hasNextPage,
  hasPreviousPage,
  fetchNextPage,
  fetchPreviousPage,
}) => {
  useEffect(() => {
    console.log("table", data);
  }, [data]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <div className="flex h-full w-full flex-col">
      <div className="overflow-x-auto rounded-lg">
        <div className="max-h-[calc(100vh-200px)] overflow-y-auto">
          <table className="w-full divide-y divide-gray-200">
            <thead className="sticky top-0 border-l border-r border-t bg-container-light">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="cursor-pointer bg-bg-light px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {table.getRowModel().rows.map((row, index) => (
                <tr
                  key={row.id}
                  className={`bg-container-light hover:bg-gray-50`}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className="whitespace-nowrap px-4 py-2 text-sm text-gray-500"
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between px-4">
        <button
          className="rounded border px-4 py-2 disabled:opacity-50"
          onClick={() => fetchPreviousPage()}
          disabled={!!!hasPreviousPage}
        >
          Previous
        </button>
        <span className="text-sm text-gray-700">
          Page {currentPage} of {maxPage}
        </span>
        <button
          className="rounded border px-4 py-2 disabled:opacity-50"
          onClick={() => fetchNextPage()}
          disabled={!!!hasNextPage}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default Tables;
