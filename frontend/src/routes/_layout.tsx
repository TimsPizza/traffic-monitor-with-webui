import React, { useEffect, useRef, useState, useCallback } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
// import Header from "../components/Header"; // Header seems unused now
import { WindowSizeContext } from "../App";
import { EMediaBreakpoints } from "../types/ui/types";
import Header from "../components/Header";
// Removed PiBinaryLight import as it's moved to Sidebar
// Removed duplicate imports below

const Layout = () => {
  const navigate = useNavigate();
  const { breakpoint } = React.useContext(WindowSizeContext); // Keep only one declaration
  const [shouldSidebarCollapse, setShouldSidebarCollapse] = useState(false); // Simplified state setter name
  const [showOverlay, setShowOverlay] = useState(false);

  const toggleSidebarCollapse = useCallback(() => {
    // Use useCallback for stability if passed down deeply
    setShouldSidebarCollapse((prev) => {
      const nextState = !prev;
      // Only show overlay on mobile when expanding the sidebar
      if (breakpoint <= EMediaBreakpoints.lg) {
        setShowOverlay(nextState === false); // Show overlay if sidebar is NOT collapsed (i.e., expanded)
      }
      console.log("Sidebar toggled:", nextState);
      return nextState;
    });
  }, [breakpoint]); // Dependency on breakpoint to re-create toggle logic if breakpoint changes
  const sidebarRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    navigate("/dashboard");
  }, []);
  useEffect(() => {
    const shouldCollapse = breakpoint <= EMediaBreakpoints.lg;
    setShouldSidebarCollapse(shouldCollapse);
    // Hide overlay if screen becomes larger than lg while sidebar is expanded
    if (!shouldCollapse && showOverlay) {
      setShowOverlay(false);
    }
  }, [breakpoint]);

  return (
    <div
      id="layout"
      className="relative flex min-h-screen flex-row bg-bg-light dark:!bg-gray-900"
    >
      <div
        id="mobile-overlay"
        className={`fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity duration-200 lg:hidden ${showOverlay ? "opacity-100" : "pointer-events-none opacity-0"}`}
        // onClick={() => {
        //   setShouldSidebarCollapse(true);
        //   setShowOverlay(false);
        // }}
      />
      <div
        id="sidebar-wrapper"
        ref={sidebarRef}
        // Apply width transition and dynamic width classes
        className={`fixed z-50 h-screen overflow-y-auto overflow-x-hidden bg-container-light transition-all duration-300 ease-in-out lg:static lg:h-auto lg:overflow-visible dark:!bg-gray-800 ${shouldSidebarCollapse ? "w-20" : "w-64"} ${breakpoint <= EMediaBreakpoints.lg && shouldSidebarCollapse ? "-translate-x-full" : "translate-x-0"} lg:translate-x-0`} // Handle mobile slide-in/out
      >
        <Sidebar
          toggleSidebarCollapse={toggleSidebarCollapse}
          shouldSidebarCollapse={shouldSidebarCollapse}
        />
      </div>
      <div
        id="content-wrapper"
        className="flex w-full flex-1 flex-col overflow-auto bg-bg-light dark:!bg-gray-900" // Ensure dark bg applies here too
      >
        <div
          id="layout-content-wrapper"
          className={`rounded-lg border !bg-container-light lg:mx-2`}
        >
          <div
            className={`flex-1 rounded-lg ${breakpoint >= EMediaBreakpoints.lg ? "p-1" : ""} `}
          >
            <Header
              shouldSidebarCollapse={shouldSidebarCollapse}
              toggleSidebarCollapse={toggleSidebarCollapse}
            />
            <Outlet />
          </div>
        </div>
        <footer className="h-[8%] p-1">
          <Footer />
        </footer>
      </div>
    </div>
  );
};

export default Layout;
