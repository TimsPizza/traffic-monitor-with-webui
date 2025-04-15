import React from "react";
import { useLocation } from "react-router-dom";

interface HeaderProps {
  shouldSidebarCollapse: boolean;
  toggleSidebarCollapse: () => void;
}

const Header: React.FC<HeaderProps> = ({
  shouldSidebarCollapse,
  toggleSidebarCollapse,
}) => {
  const { pathname } = useLocation();
  return (
    <header className="relative mt-1 flex min-h-12 flex-row items-center bg-container-light p-1">
      <button
        id="sidebar-toggler"
        className={`ml-auto block scale-[1.2] p-2 text-xl lg:ml-6 dark:text-white`}
        // Use ml-auto for better positioning when title hides
        onClick={toggleSidebarCollapse}
      >
        <i
          className={`bi ${shouldSidebarCollapse ? "bi-justify-right" : "bi-justify-left"}`}
        ></i>
      </button>
      <h3 className="text-3xl font-bold capitalize">
        #{pathname.split("/").at(-1)}
      </h3>
    </header>
  );
};

export default Header;
