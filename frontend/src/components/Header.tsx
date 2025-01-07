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
      className={`h-full w-full rounded-md border border-gray-300`}
      id="header-container"
      ref={headerRef}
    >
      <span className="">Header PlaceHolder</span>
    </div>
  );
};

export default Header;
