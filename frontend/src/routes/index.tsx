import { createHashRouter, RouteObject } from "react-router-dom";
import Layout from "./_layout";
import Dashboard from "../pages/Dashboard";
const routes: RouteObject[] = [
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/dashboard",
        element: <Dashboard />,
        children: [],
      },
    ],
  },
];
export const router = createHashRouter(routes);
