import React, { useState } from "react";
import { NavLink } from "react-router-dom";

const Sidebar: React.FC<{
  shouldSidebarCollapse: boolean;
  setShouldSidebarCollapse: (val: boolean) => void;
}> = ({ shouldSidebarCollapse, setShouldSidebarCollapse }) => {
  const navItems = [
    { path: "/dashboard", icon: "bi-house-fill", label: "Dashboard" },
    { path: "/settings", icon: "bi-gear-fill", label: "Settings" },
    { path: "/analytics", icon: "bi-graph-up", label: "Analytics" },
    { path: "/reports", icon: "bi-file-earmark-text-fill", label: "Reports" },
  ];
  return (
    <div className={`h-full bg-container-light`}>
      <div className="flex h-[92%] flex-col space-y-1 p-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `relative flex origin-center items-center justify-center rounded-lg p-2 text-blue-700 transition-transform duration-300 before:absolute before:left-0 before:top-1/2 before:h-7 before:w-12 before:-translate-x-[110%] before:-translate-y-1/2 before:rounded-md before:bg-tw-primary hover:bg-gray-200 ${
                isActive
                  ? "before:scale-y-100"
                  : "text-gray-700 before:scale-y-0"
              }`
            }
            onClick={() => setShouldSidebarCollapse(true)}
          >
            <span className="mx-auto flex aspect-[4/3] w-12 items-center justify-center rounded-lg bg-tw-primary text-white">
              <i
                className={`bi ml-2 ${item.icon} text-md mx-auto scale-95 text-xl`}
              />
            </span>
            <div
              className={`${shouldSidebarCollapse ? "w-0" : "ml-2 w-24"} origin-left overflow-hidden transition-all duration-200`}
            >
              <span>{item.label}</span>
            </div>
          </NavLink>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
