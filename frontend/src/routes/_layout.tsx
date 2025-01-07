import React, { useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Nav from "../components/Nav";
import Footer from "../components/Footer";
import Header from "../components/Header";

const Layout = () => {
  const navigate = useNavigate();
  useEffect(() => {
    navigate("/dashboard");
  }, []);
  return (
    <div id="layout" className="relative flex flex-row">
      <div
        id="sidebar-wrapper"
        className="h-screen w-1/5 border !border-red-300 p-1"
      >
        <nav className="sticky left-0 top-0 z-50 h-full border !border-red-300 p-1">
          <Nav />
        </nav>
      </div>
      <div
        id="content-wrapper"
        className="flex h-full w-full flex-col border !border-red-300"
      >
        <header className="h-[8%] p-1">
          <Header />
        </header>
        <div
          id="layout-content-wrapper"
          className="flex-1 border !border-red-300 p-1"
        >
          <Outlet />
        </div>
        <footer className="h-[8%] border !border-red-300 p-1">
          <Footer />
        </footer>
      </div>
    </div>
  );
};

export default Layout;
