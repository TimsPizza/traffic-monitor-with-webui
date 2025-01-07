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
    <div id="layout" className="flex h-full w-full flex-col">
      <div id="header-wrapper" className="border !border-red-300 p-1">
        <header className="">
          <Header />
        </header>
      </div>
      <div
        id="content-wrapper"
        className="flex h-full w-full flex-row border !border-red-300"
      >
        <nav className="w-[15%] border !border-red-300 p-1">
          <Nav />
        </nav>
        <div
          id="layout-content-wrapper"
          className="flex-1 border !border-red-300 p-1"
        >
          <Outlet />
        </div>
      </div>
      <footer className="min-h-[8%] border !border-red-300 p-1">
        <Footer />
      </footer>
    </div>
  );
};

export default Layout;
