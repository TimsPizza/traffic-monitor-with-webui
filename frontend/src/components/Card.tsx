import React, { useEffect } from "react";
import {
  EChartType,
  TColorPalette,
  TChartData,
  DEFAULT_COLOR_PALETTES,
} from "../client/types";
import Chart from "./Chart";

interface ICardProps {
  title?: string;
  data?: string | TChartData[];
  type?: EChartType | "classic";
  colorPalette?: TColorPalette;
}

const Card: React.FC<ICardProps> = ({
  title: title_ = "Default Title",
  data: data_ = "Default Data",
  type: cardType = "classic",
  // title uses index 0 of colorPalette, pass the slice[1:] to Chart component
  colorPalette = DEFAULT_COLOR_PALETTES[0],
}) => {
  const [title, setTitle] = React.useState("");
  const [data, setData] = React.useState<string | TChartData[]>("");
  const [timeRange, setTimeRange] = React.useState();
  useEffect(() => {
    setTitle(title_);
    setData(data_);
    return () => {};
  }, [title_, data_]);

  return (
    <div
      id="card-wrapper"
      className={`flex max-h-72 min-h-36 flex-col justify-center rounded-md border border-gray-300 bg-[#F3F4F6]`}
      style={{ boxShadow: "3px 3px 3px -4px #000000", color: colorPalette[0] }}
    >
      {cardType === "classic" ? (
        <>
          <div
            id="card-title"
            className="w-full self-start border-b border-gray-300 p-1"
          >
            <span className="text-2xl font-bold">{title}</span>
          </div>
          <div id="card-data" className="flex-1">
            <span className="text-lg">
              {typeof data === "string" ? data : "Invalid data"}
            </span>
          </div>
          ƒ
        </>
      ) : (
        <div className="h-full w-full">
          <Chart
            chartType={cardType}
            title={title}
            data={Array.isArray(data) ? data : []}
            colorPalette={colorPalette}
            bordered={false}
          />
        </div>
      )}
    </div>
  );
};

export default Card;
