import React from "react";
import { FiArrowUpRight, FiArrowDownRight } from "react-icons/fi";

export interface ICardData {
  loading: boolean;
  data: { 
    [key: string]: number | string | undefined;
    trend?: number; // 新增趋势数据
  };
}

interface ICardProps {
  title?: string;
  data?: ICardData;
  color?: string;
}

const Card: React.FC<ICardProps> = ({
  title = "Default Title",
  data = { loading: false, data: { default: 0 } },
  color = "from-blue-500 to-blue-600",
}) => {
  // Loading skeleton animation class
  const skeletonClass = "animate-pulse bg-gray-200 rounded";
  
  // Helper function to render trend indicator
  const renderTrend = (trend?: number) => {
    if (trend === undefined) return null;
    const isPositive = trend >= 0;
    const Icon = isPositive ? FiArrowUpRight : FiArrowDownRight;
    return (
      <div className={`flex items-center gap-1 text-sm ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
        <Icon className="h-4 w-4" />
        <span>{Math.abs(trend)}%</span>
      </div>
    );
  };

  return (
    <div
      className="relative h-full w-full overflow-hidden rounded-xl bg-white p-6 shadow-lg transition-all duration-300 hover:shadow-xl dark:bg-gray-800"
    >
      {/* Decorative gradient element */}
      <div className={`absolute -right-4 -top-4 h-24 w-24 rotate-12 rounded-full bg-gradient-to-br ${color} opacity-10`} />
      
      {/* Card Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${color}`}>
            <span className="text-lg font-semibold text-white">
              {title[0]}
            </span>
          </div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
            {title}
          </h3>
        </div>
        {!data.loading && renderTrend(data.data.trend)}
      </div>

      {/* Card Content */}
      <div className="space-y-4">
        {data.loading ? (
          // Loading skeleton
          <>
            <div className={`h-4 w-2/3 ${skeletonClass}`} />
            <div className={`h-4 w-1/2 ${skeletonClass}`} />
          </>
        ) : (
          Object.entries(data.data).map(([key, value]) => {
            if (key === 'trend') return null; // Skip trend in main content
            return (
              <div key={key} className="flex flex-col">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400 capitalize">
                  {key}
                </span>
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  {value}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Card;
