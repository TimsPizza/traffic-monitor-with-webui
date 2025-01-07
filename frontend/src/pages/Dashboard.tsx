import React from "react";
import { Row, Col } from "react-bootstrap";
import Card from "../components/Card";
import Chart from "../components/Chart";
import { EChartType } from "../client/types";
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
      <Row>
        <Col sm={6} className="grid grid-cols-2 gap-2">
          <Card
            type={EChartType.POLY_LINE}
            title="PolyLine Chart Card Test"
            data={polylineData}
          />
          <Card
            type={EChartType.RADIAL_BAR}
            title="Radial Chart Card Test"
            data={radialBarData}
          />
          <Card
            type={EChartType.SMOOTH_LINE}
            title="SmoothLine Chart Card Test"
            data={smoothLineData}
          />
          <Card
            type={EChartType.PIE}
            title="Pie Chart Card Test"
            data={pieData}
          />
        </Col>
        <Col sm={6}>
          <Chart
            chartType={EChartType.PIE}
            title="Pie Chart Test"
            data={pieData}
          />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
