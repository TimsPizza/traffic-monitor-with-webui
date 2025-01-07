import React from "react";
import { Row, Col } from "react-bootstrap";
import Card from "../components/Card";
import Chart from "../components/Chart";
import { DEFAULT_COLOR_PALETTES, EChartType } from "../client/types";
import {
  pieData,
  polylineData,
  radialBarData,
  smoothLineData,
} from "../fakedata";

const Dashboard = () => {
  return (
    <div
      id="dashboard-wrapper"
      className="h-full w-full rounded-md border border-gray-300"
    >
      <Row className="h-2/5">
        <Col sm={6} className="grid grid-cols-2 gap-2">
          <Card
            type={EChartType.POLY_LINE}
            title="PolyLine Chart Card Test"
            data={polylineData}
            colorPalette={DEFAULT_COLOR_PALETTES[0]}
          />
          <Card
            type={EChartType.RING}
            title="Ring Chart Card Test"
            data={radialBarData}
            colorPalette={DEFAULT_COLOR_PALETTES[1]}
          />
          <Card
            type={EChartType.SMOOTH_LINE}
            title="SmoothLine Chart Card Test"
            data={smoothLineData}
            colorPalette={DEFAULT_COLOR_PALETTES[2]}
          />
          <Card
            type={EChartType.PIE}
            title="Pie Chart Card Test"
            data={pieData}
            colorPalette={DEFAULT_COLOR_PALETTES[3]}
          />
        </Col>
        <Col sm={6}>
          <Chart
            chartType={EChartType.SMOOTH_LINE}
            title="SmoothLine Card Test"
            data={smoothLineData}
            colorPalette={DEFAULT_COLOR_PALETTES[3]}
          />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
