import React, { useEffect, useRef, useState } from "react";

const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const headerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 48) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);
  return (
    <div
      className={`flex h-full w-full items-center justify-center rounded-md border border-gray-300`}
      id="header-container"
      ref={headerRef}
    >
      <span className="text-center">Header PlaceHolder</span>
      <i className="bi bi-house text-2xl ml-4"></i>
    </div>
  );
};

export default Header;
