import React, { useEffect, useRef, useState, useCallback } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import Header from "../components/Header";
import { WindowSizeContext } from "../App";
import { EMediaBreakpoints } from "../client/types";

const Layout = () => {
  const navigate = useNavigate();
  const { breakpoint } = React.useContext(WindowSizeContext);
  const [shouldSidebarCollapse, setShouldSidebarCollapse_] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const setShouldSidebarCollapse = (val: boolean) => {
    setShouldSidebarCollapse_(val);
    setShowOverlay(!val);
  };

  const toggleSidebarCollapse = () => {
    setShouldSidebarCollapse(!shouldSidebarCollapse);
  };
  const sidebarRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    navigate("/dashboard");
  }, []);
  useEffect(() => {
    const shouldCollapse = breakpoint <= EMediaBreakpoints.lg;
    setShouldSidebarCollapse(shouldCollapse);
    if (!shouldCollapse) {
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
        onClick={() => {
          setShouldSidebarCollapse(true);
          setShowOverlay(false);
        }}
      />
      <div
        id="sidebar-wrapper"
        ref={sidebarRef}
        className={`fixed mx-1 my-2 mt-0 h-screen overflow-hidden dark:!bg-gray-800 transition-transform duration-200 ease-linear lg:static lg:h-full lg:translate-x-0`}
      >
        <div className="block w-full">
          <button
            id="sidebar-toggler"
            className={`bi bi-justify-left ml-6 block scale-[1.2] p-2 text-xl dark:text-white`}
            onClick={toggleSidebarCollapse}
          />
        </div>
        <nav className="left-0 top-0 z-50 h-full w-full flex-1">
          <Sidebar
            setShouldSidebarCollapse={setShouldSidebarCollapse}
            shouldSidebarCollapse={shouldSidebarCollapse}
          />
        </nav>
      </div>
      <div
        id="content-wrapper"
        className="flex w-full flex-1 flex-col overflow-auto"
      >
        {/* <header className="relative mt-1 min-h-[5%] p-1">
          <div
            id="sidebar-toggle"
            className={`absolute left-0 top-1/2 z-50 h-8 w-8 -translate-y-1/2 translate-x-1/2 rounded-lg border border-gray-300 text-center transition-transform duration-300 ${shouldSidebarCollapse ? "" : "hidden"} lg:hidden`}
            onClick={() => {
              setShouldSidebarCollapse(false);
              setShowOverlay(true);
            }}
          >
            <i className={`bi bi-list text-xl`} />
          </div>
          <Header />
        </header> */}
        <div id="layout-content-wrapper" className="flex-1 p-1">
          <Outlet />
        </div>
        <footer className="h-[8%] p-1">
          <Footer />
        </footer>
      </div>
    </div>
  );
};

export default Layout;
