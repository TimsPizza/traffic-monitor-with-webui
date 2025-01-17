import React, { useState } from "react";
import { Link } from "react-router-dom";

const Nav: React.FC<{
  shouldSidebarCollapse: boolean;
  setShouldSidebarCollapse: (val: boolean) => void;
}> = ({ shouldSidebarCollapse, setShouldSidebarCollapse }) => {
  const navItems = [
    { path: "/", icon: "bi-house", label: "Dashboard" },
    { path: "/settings", icon: "bi-gear", label: "Settings" },
    { path: "/analytics", icon: "bi-graph-up", label: "Analytics" },
    { path: "/reports", icon: "bi-file-earmark-text", label: "Reports" },
  ];
  return (
    <div className={`h-full bg-[#F3F4F6]`}>
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
          <Link
            key={item.path}
            to={item.path}
            className="flex items-center space-x-3 rounded-lg p-2 hover:bg-gray-200"
            onClick={() => setShouldSidebarCollapse(true)}
          >
            <i className={`bi ${item.icon} text-xl`} />
            <span>{item.label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Nav;
