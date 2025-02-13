import React, { useEffect } from "react";

interface IDropdownProps {
  label: string;
  options: string[];
  selected: string
  handleSelect: (selected: string) => void;
  minW?: string;
}

const Dropdown: React.FC<IDropdownProps> = ({
  label,
  options = [],
  selected = "",
  handleSelect,
  minW,
}) => {
  const [componentUniqueID, _] = React.useState<string>(
    Math.random().toString(36).substring(7),
  );
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [expanded, setExpanded] = React.useState<boolean>(false);
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent): void => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setExpanded(false);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);
  return (
    <div
      className={`relative flex h-full`}
      style={minW ? { minWidth: minW } : {}}
      ref={containerRef}
    >
      <label
        htmlFor={`dropdown-toggle-${componentUniqueID}`}
        className={`relative flex w-full cursor-pointer items-center justify-center rounded-md bg-blue-500 px-2 transition-all hover:bg-blue-400 active:bg-blue-600 ${expanded ? "rounded-b-none" : ""}`}
        onClick={() => setExpanded(!expanded)}
      >
        <span className="text-white">{selected ?? label}</span>
        <i
          className={`bi bi-chevron-down ml-2 text-white transition-transform duration-200 ${expanded ? "-rotate-180" : ""} `}
        />
      </label>

      <ul
        className={`absolute left-0 top-10 z-[2] w-full origin-top scale-y-0 cursor-pointer rounded-b-md text-left shadow-md transition-transform duration-200 ${expanded ? "scale-y-100" : "scale-y-0"}`}
      >
        {options.map((option, index) => (
          <label
            htmlFor={`dropdown-toggle-${componentUniqueID}`}
            key={option}
            className={`w-full cursor-pointer bg-container-light p-2 hover:bg-gray-200 ${
              index === options.length - 1 ? "rounded-b-md" : ""
            }`}
            onClick={() => {
              setExpanded(false);
              handleSelect(option);
            }}
          >
            {option}
          </label>
        ))}
      </ul>
    </div>
  );
};

export default Dropdown;
