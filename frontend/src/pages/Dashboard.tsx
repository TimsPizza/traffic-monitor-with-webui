import React from "react";
import { Row, Col } from "react-bootstrap";
import Card from "../components/Card";

const Dashboard = () => {
  return (
    <div id="dashboard-wrapper" className="">
      <Row>
        <Col sm={6}>
          <Row>
            <Col sm={12}>
              <Card />
            </Col>
          </Row>
          <Row>
            <Col sm={12}>
              <Card />
            </Col>
          </Row>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
