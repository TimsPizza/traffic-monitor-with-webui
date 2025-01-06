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
      <div className="">
        <header className="">
          <Header />
        </header>
      </div>
      <div className="flex h-full w-full flex-row">
        <nav className="w-[15%]">
          <Nav />
        </nav>
        <div id="layout-content-wrapper" className="flex-1">
          <Outlet />
        </div>
      </div>
      <footer className="min-h-[8%]">
        <Footer />
      </footer>
    </div>
  );
};

export default Layout;
