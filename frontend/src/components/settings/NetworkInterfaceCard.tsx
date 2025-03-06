import React, { useEffect, useState } from "react";
import { FiWifi } from "react-icons/fi";
import { configService } from "../../client/services/config";
import { useQuery } from "react-query";
import useToast from "../../hooks/useToast";

const NetworkInterfaceCard: React.FC = () => {
  const [interfaces, setInterfaces] = useState<string[]>([]);
  const [selectedInterface, setSelectedInterface] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();
  const query = useQuery({
    queryKey: "interfaces",
    queryFn: configService.getInterfaces,
    onSuccess: (data) => {
      console.log(data);
      setInterfaces(data.interfaces);
      setSelectedInterface(data.selected);
    },
    onError: (error) => {
      console.error("Failed to load network interfaces:", error);
      setError("Failed to load network interfaces");
      toast.error("Failed to load network interfaces");
    },
    refetchInterval: false,
    retry: 3,
  });

  useEffect(() => {}, []);

  const handleInterfaceChange = async (interfaceName: string) => {
    try {
      setSelectedInterface(interfaceName);
      const success = await configService.setInterface(interfaceName);
      if (success) {
        toast.success(`Successfully set network interface to ${interfaceName}`);
      } else {
        toast.error(`Failed to set network interface to ${interfaceName}`);
      }
    } catch (error) {
      console.error("Failed to set network interface:", error);
    }
  };

  return (
    <div className="rounded-xl bg-white p-6 shadow-lg transition-all min-h-48 duration-300 hover:shadow-xl dark:bg-gray-800">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-blue-600">
          <FiWifi className="h-6 w-6 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          Network Interface
        </h3>
      </div>

      {query.isLoading ? (
        <div className="animate-pulse space-y-3">
          <div className="h-10 w-full rounded-lg bg-gray-200 dark:bg-gray-700" />
        </div>
      ) : query.isError ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-600 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          <select
            value={selectedInterface}
            onChange={(e) => handleInterfaceChange(e.target.value)}
            className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-gray-700 focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
          >
            {interfaces.map((iface) => (
              <option key={iface} value={iface}>
                {iface}
              </option>
            ))}
          </select>

          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <span className="inline-flex h-2 w-2 rounded-full bg-green-500" />
            <span>Currently capturing on: {selectedInterface}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default NetworkInterfaceCard;
