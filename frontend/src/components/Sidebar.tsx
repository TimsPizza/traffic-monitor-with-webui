import React, { useState } from "react";
import { NavLink } from "react-router-dom";

const Sidebar: React.FC<{
  shouldSidebarCollapse: boolean;
  setShouldSidebarCollapse: (val: boolean) => void;
}> = ({ shouldSidebarCollapse, setShouldSidebarCollapse }) => {
  const navItems = [
    { path: "/dashboard", icon: "bi-house", label: "Dashboard" },
    { path: "/settings", icon: "bi-gear", label: "Settings" },
    { path: "/analytics", icon: "bi-graph-up", label: "Analytics" },
    { path: "/reports", icon: "bi-file-earmark-text", label: "Reports" },
  ];
  return (
    <div className={`h-full bg-container-light`}>
      <div
        id="topper"
        className="flex h-[8%] flex-row items-center justify-center gap-4 px-3"
      >
        <i id="logo" className="bi bi-box-fill text-3xl" />
        <span id="brand" className="text-xl font-bold">
          The App
        </span>
      </div>

      <div className="flex h-[92%] flex-col space-y-1 p-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 rounded-lg p-2 hover:bg-gray-200 ${
                isActive ? "text-blue-700" : "text-gray-700"
              }`
            }
            onClick={() => setShouldSidebarCollapse(true)}
          >
            <i className={`bi ml-2 ${item.icon} text-xl`} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
