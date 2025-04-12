import React, { useEffect, useState } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";
import { HeatmapDataPoint } from "../../../types/hooks/types";
import { scaleLinear } from "d3-scale";
import { bytesToSize } from "../../../utils/tools";
import geoData from "../../../assets/countries-50m.json"; // Import local file
import { NAME_TO_ISO_MAP } from "../../../utils/countryMap";

// Mapping from full country name (from geojson) to ISO A2 code (expected in dataMap keys)

interface TooltipProps {
  show: boolean;
  content: string;
  position: { x: number; y: number };
}

const Tooltip: React.FC<TooltipProps> = ({ show, content, position }) => {
  if (!show) return null;

  return (
    <div
      className="pointer-events-none absolute z-10 rounded bg-black/75 p-2 text-xs text-white"
      style={{
        left: position.x,
        top: position.y,
        transform: "translate(-50%, -100%)",
        whiteSpace: "pre-line",
      }}
    >
      {content}
    </div>
  );
};

const WorldMap: React.FC<{
  data?: HeatmapDataPoint[];
  loading?: boolean;
}> = ({ data = [], loading = false }) => {
  const [tooltip, setTooltip] = useState<TooltipProps>({
    show: false,
    content: "",
    position: { x: 0, y: 0 },
  });
  useEffect(() => {
    console.log("WorldMap data", data);
  }, [data]);

  // 计算数值范围
  const valueExtent = React.useMemo(() => {
    if (!data.length) return [0, 1];
    const values = data.map((d) => d.value || 0);
    const max = Math.max(...values);
    return [0, max];
  }, [data]);

  // 创建颜色比例尺
  const colorScale = React.useMemo(
    () =>
      scaleLinear<string>()
        .domain([0, valueExtent[1]])
        .range(["#ffedea", "#ff5233"]),
    [valueExtent],
  );

  // 创建国家ID到数据的映射
  const dataMap = React.useMemo(() => {
    const map = data.reduce(
      (acc, item) => {
        acc[item.id] = item;
        return acc;
      },
      {} as Record<string, HeatmapDataPoint>,
    );
    console.log("New dataMap:", map);
    return map;
  }, [data]);

  if (loading) {
    return (
      <div className="w-full h-full bg-gray-300 animate-pulse">
        {/* <span className="text-gray-500">加载中...</span> */}
      </div>
    );
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (tooltip.show) {
      setTooltip((prev) => ({
        ...prev,
        position: { x: e.clientX, y: e.clientY - 10 },
      }));
    }
  };

  const handleMouseEnter =
    (geo: any, countryData?: HeatmapDataPoint) => (e: any) => {
      const countryName = geo.properties.name; // Get full name from geojson properties
      const countryIsoA2 = NAME_TO_ISO_MAP[countryName]; // Map name to ISO A2 code

      // Use the mapped ISO A2 code to look up data
      const actualCountryData = countryIsoA2
        ? dataMap[countryIsoA2]
        : undefined;

      // Only show tooltip if we have data for the mapped country code
      if (!actualCountryData || !countryIsoA2) return;

      const content = `${countryName} (${countryIsoA2})
流量: ${bytesToSize(actualCountryData.metadata?.totalBytes || 0).size} ${bytesToSize(actualCountryData.metadata?.totalBytes || 0).unit}
数据包: ${actualCountryData.metadata?.totalPackets?.toLocaleString() || 0}`;

      setTooltip({
        show: true,
        content,
        position: { x: e.clientX, y: e.clientY - 10 },
      });
    };

  return (
    <div
      className="relative h-[400px] w-full overflow-hidden"
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setTooltip((prev) => ({ ...prev, show: false }))}
    >
      <ComposableMap
        width={800}
        height={320}
        projection="geoMercator"
        projectionConfig={{
          scale: 60, // Reduced scale
          center: [0, 40], // Centered horizontally
        }}
        style={{
          width: "100%",
          height: "100%", // Corrected height back to 100%
        }}
      >
        <ZoomableGroup>
          <Geographies geography={geoData}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const countryName = geo.properties.name; // Get full name from geojson properties
                const countryIsoA2 = NAME_TO_ISO_MAP[countryName]; // Map name to ISO A2 code
                const countryData = countryIsoA2
                  ? dataMap[countryIsoA2]
                  : undefined; // Look up data using the mapped ISO A2 code
                const fillColor = countryData
                  ? colorScale(countryData.value)
                  : "#EAEAEC";

                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={fillColor}
                    stroke="#D6D6DA"
                    strokeWidth={0.5}
                    // Pass the actual looked-up countryData to handleMouseEnter
                    onMouseEnter={handleMouseEnter(geo, countryData)}
                    style={{
                      default: {
                        outline: "none",
                      },
                      hover: {
                        fill: countryData
                          ? colorScale(countryData.value * 1.1)
                          : "#F5F5F5",
                        outline: "none",
                        cursor: "pointer",
                      },
                    }}
                  />
                );
              })
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>

      <Tooltip {...tooltip} />

      {/* 图例 */}
      <div className="absolute bottom-4 right-4 rounded bg-white/80 p-2 shadow-md">
        <div className="flex items-center space-x-2">
          <div
            className="h-4 w-20 rounded"
            style={{
              background: "linear-gradient(90deg, #ffedea 0%, #ff5233 100%)",
            }}
          />
          <div className="flex items-center space-x-4">
            <span className="text-sm">低</span>
            <span className="text-sm">流量分布</span>
            <span className="text-sm">高</span>
          </div>
        </div>
        <div className="mt-1 text-xs text-gray-500">
          {`范围: ${bytesToSize(valueExtent[0]).size} ${bytesToSize(valueExtent[0]).unit} - ${bytesToSize(valueExtent[1]).size} ${bytesToSize(valueExtent[1]).unit}`}
        </div>
      </div>
    </div>
  );
};

export default WorldMap;
