import React from "react";
import { Row, Col } from "react-bootstrap";
import Card from "../components/Card";
import Chart from "../components/Chart";
import { DEFAULT_COLOR_PALETTES, EChartType } from "../client/types";
import {
  accessRecordData,
  pieData,
  polylineData,
  radialBarData,
  smoothLineData,
} from "../fakedata";
import Tables from "../components/Tables";

const Dashboard = () => {
  return (
    <div
      id="dashboard-wrapper"
      className="h-full w-full rounded-md"
    >
      <Row className="px-2 mt-2">
        <Col
          id="cards-wrapper"
          md={12}
          lg={6}
          className="mb-2 grid grid-cols-2 gap-2"
        >
          <Card
            type={EChartType.POLY_LINE}
            title="PolyLine Chart Card Test"
            data={polylineData}
            colorPalette={DEFAULT_COLOR_PALETTES[3]}
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
            colorPalette={DEFAULT_COLOR_PALETTES[4]}
          />
          <Card
            type={EChartType.PIE}
            title="Pie Chart Card Test"
            data={pieData}
            colorPalette={DEFAULT_COLOR_PALETTES[3]}
          />
        </Col>
        <Col id="charts-container" md={12} lg={6} className="mb-2">
          <Chart
            chartType={EChartType.SMOOTH_LINE}
            title="SmoothLine Card Test"
            data={smoothLineData}
            colorPalette={DEFAULT_COLOR_PALETTES[3]}
          />
        </Col>
        <Col id="table-wrapper" sm={6} md={12} className="mb-2">
          <Tables data={accessRecordData} />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
