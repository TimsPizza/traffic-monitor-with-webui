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
      className="relative flex min-h-screen flex-row bg-bg-light"
    >
      <div
        id="overlay"
        className={`fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity duration-200 ${showOverlay ? "opacity-100" : "pointer-events-none opacity-0"}`}
        onClick={() => {
          setShouldSidebarCollapse(true);
          setShowOverlay(false);
        }}
      ></div>
      <div
        id="sidebar-wrapper"
        ref={sidebarRef}
        className={`fixed h-screen w-[256px] overflow-hidden rounded-r-lg my-2 transition-transform duration-200 ease-linear lg:static lg:h-full lg:translate-x-0 lg:rounded-l-lg ${shouldSidebarCollapse ? "-translate-x-[256px]" : "z-50"} `}
      >
        <nav className="left-0 top-0 z-50 h-full w-full">
          <Sidebar
            setShouldSidebarCollapse={setShouldSidebarCollapse}
            shouldSidebarCollapse={shouldSidebarCollapse}
          />
        </nav>
      </div>
      <div
        id="content-wrapper"
        className="flex w-full flex-1 flex-col overflow-y-auto"
      >
        <header className="relative min-h-[5%] p-1 mt-1">
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
        </header>
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
