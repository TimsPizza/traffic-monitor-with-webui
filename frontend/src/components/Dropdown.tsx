import React from "react";

interface IDropdownProps {
  label: string;
  options: string[];
  handleSelect: (selected: string) => void;
}

const Dropdown: React.FC<IDropdownProps> = ({
  label = "dropdown",
  options = [],
  handleSelect,
}) => {
  const [selected, setSelected] = React.useState<string>(label);
  const componentUniqueID = React.useState<string>(
    Math.random().toString(36).substring(7),
  );
  return (
    <div className="relative flex h-full">
      {/* Hidden Checkbox */}
      <input
        type="checkbox"
        id={`dropdown-toggle-${componentUniqueID}`}
        className={`peer hidden`}
      />

      {/* Trigger */}
      <label
        htmlFor={`dropdown-toggle-${componentUniqueID}`}
        className="relative flex cursor-pointer items-center justify-center rounded-md bg-blue-500 px-2 transition-all hover:bg-blue-400 active:bg-blue-600 peer-checked:rounded-b-none"
      >
        <span className="text-white">{selected}</span>
        <i className="bi bi-chevron-down ml-2 text-white transition-transform duration-200 peer-checked:rotate-180" />
      </label>
      {/* Overlay for clicking outside */}
      <label
        htmlFor={`dropdown-toggle-${componentUniqueID}`}
        className="fixed inset-0 z-[1] hidden peer-checked:block"
      ></label>

      {/* Dropdown Menu */}
      <ul className="absolute left-0 top-10 z-[2] w-full origin-top scale-y-0 cursor-pointer rounded-b-md shadow-md transition-transform duration-200 peer-checked:scale-y-100">
        {options.map((option, index) => (
          <label
            htmlFor={`dropdown-toggle-${componentUniqueID}`}
            key={option}
            className={`w-full cursor-pointer bg-container-light p-2 hover:bg-gray-200 ${
              index === options.length - 1 ? "rounded-b-md" : ""
            }`}
            onClick={() => {
              setSelected(option);
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
