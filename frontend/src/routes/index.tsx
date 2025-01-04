import { createHashRouter, RouteObject } from "react-router-dom";
import Layout from "./_layout";
const routes: RouteObject[] = [
  {
    path: "/",
    element: <Layout />,
    children: [],
  },
];
export const router = createHashRouter(routes);