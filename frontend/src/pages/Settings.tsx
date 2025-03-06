import React, { useCallback } from "react";
import NetworkInterfaceCard from "../components/settings/NetworkInterfaceCard";
import ProtocolRulesCard from "../components/settings/ProtocolRulesCard";
import FilterRulesCard from "../components/settings/FilterRulesCard";

const Settings = () => {

  return (
    <div className="min-h-screen w-full bg-gray-50 p-6 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Settings
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Configure capture settings, protocol rules, and filters
          </p>
        </div>

        {/* Settings Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Network Interface Section */}
          <div className="w-full">
            <NetworkInterfaceCard />
          </div>

          {/* Protocol Rules Section */}
          <div className="w-full">
            <ProtocolRulesCard />
          </div>

          {/* Filter Rules Section - Full Width */}
          <div className="w-full lg:col-span-2">
            <FilterRulesCard />
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
          Changes are applied immediately and persisted across sessions
        </div>
      </div>
    </div>
  );
};

export default Settings;
