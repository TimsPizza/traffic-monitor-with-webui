import React from "react";
import { NavLink } from "react-router-dom";
import { CiHome, CiWavePulse1, CiSettings } from "react-icons/ci";
import { PiBinaryLight } from "react-icons/pi";

const Sidebar: React.FC<{
  shouldSidebarCollapse: boolean;
  toggleSidebarCollapse: () => void;
}> = ({ shouldSidebarCollapse, toggleSidebarCollapse }) => {
  const navItems = [
    { path: "/dashboard", icon: <CiHome size={28} />, label: "Dashboard" },
    {
      path: "/analytics",
      icon: <CiWavePulse1 size={28} />,
      label: "Analytics",
    },
    { path: "/settings", icon: <CiSettings size={28} />, label: "Settings" },
    // { path: "/reports", icon: "bi-file-earmark-text-fill", label: "Reports" },
  ];

  return (
    <div className={`flex h-full flex-1 flex-col`}>
      {/* Moved Header Section */}
      <div className="flex w-full flex-row items-center justify-between px-2 py-4">
        <div
          className={`tduration-200 flex origin-left flex-row items-center gap-1 transition-all duration-200 ${shouldSidebarCollapse ? "w-10" : "w-auto"}`}
        >
          <PiBinaryLight
            className={`ml-2 flex-shrink-0 rounded-full border p-1 text-xl transition-all duration-200 dark:text-white ${shouldSidebarCollapse ? "translate-x-1/3" : ""}`}
            size={35}
          />
          {/* Animate Title Visibility */}
          <span
            className={`ml-2 origin-left whitespace-nowrap transition-opacity duration-200 ${shouldSidebarCollapse ? "max-w-0 opacity-0" : "max-w-xs opacity-100"}`}
          >
            Network Monitor
          </span>
        </div>
      </div>
      <div
        id="divider"
        className="mb-4 h-0.5 w-full origin-center scale-x-75 bg-gray-200 dark:bg-gray-600"
      />

      {/* Navigation Section */}
      <nav className="flex h-full flex-col space-y-1 p-2">
        {" "}
        {/* Adjust height calculation if needed */}
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center ${shouldSidebarCollapse ? "" : "flex-row gap-2"} ${isActive ? "border bg-bg-light dark:bg-gray-700" : ""} h-16 flex-shrink-0 rounded-lg p-2 text-gray-800 transition-all duration-200 ease-in-out last:!mt-auto hover:bg-bg-light dark:text-white dark:hover:bg-gray-700`
            }
            title={item.label} // Add title for accessibility when collapsed
          >
            <div
              className={`flex h-full flex-shrink-0 items-center text-center transition-transform duration-200 ${shouldSidebarCollapse ? "translate-x-1/3" : ""}`}
            >
              {item.icon}
            </div>
            {/* Animate Text Label Visibility */}
            <div
              className={`flex flex-shrink-0 origin-left items-center overflow-hidden whitespace-nowrap transition-all duration-200 ease-in-out ${shouldSidebarCollapse ? "ml-0 max-w-0 opacity-0" : "ml-2 max-w-xs opacity-100"}`}
            >
              <span>{item.label}</span>
            </div>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
