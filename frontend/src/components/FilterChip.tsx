interface FilterChipProps {
  filter: {
    key: string;
    value: string;
  };
  onRemove: () => void;
  className?: string;
}

const FilterChip: React.FC<FilterChipProps> = ({ filter, onRemove, className }) => {
  return (
    <div className={`inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800 ${className}`}>
      <span className="mr-2">{filter.key}: {filter.value}</span>
      <button 
        onClick={onRemove}
        className="rounded-full p-0.5 hover:bg-blue-200 transition-colors"
        aria-label="Remove filter"
      >
        <i className="bi bi-x text-lg leading-none"></i>
      </button>
    </div>
  );
};

export default FilterChip;
