import React from 'react';

export interface TimeRange {
  start: number;
  end: number;
  label: string;
  interval: number; // seconds
}

interface TimeRangeSelectorProps {
  value?: TimeRange;
  onChange?: (range: TimeRange) => void;
  loading?: boolean;
}

const PRESET_RANGES: TimeRange[] = [
  {
    label: 'Recent 1 Day',
    start: Date.now() / 1e3 - 86400,
    end: Date.now() / 1e3,
    interval: 3600, // 1 hour
  },
  {
    label: 'Recent 7 Days',
    start: Date.now() / 1e3 - 86400 * 7,
    end: Date.now() / 1e3,
    interval: 86400, // 1 day
  },
  {
    label: 'Recent 30 Days',
    start: Date.now() / 1e3 - 86400 * 30,
    end: Date.now() / 1e3,
    interval: 86400, // 1 day
  },
];

const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({
  value,
  onChange,
  loading = false,
}) => {
  return (
    <div className="flex items-center space-x-2">
      {PRESET_RANGES.map((range) => (
        <button
          key={range.label}
          onClick={() => onChange?.(range)}
          disabled={loading}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors
            ${
              value?.label === range.label
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'
            }
            ${loading ? 'cursor-not-allowed opacity-50' : ''}
          `}
        >
          {range.label}
        </button>
      ))}
    </div>
  );
};

export default TimeRangeSelector;
