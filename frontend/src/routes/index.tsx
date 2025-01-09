import { createHashRouter, RouteObject } from "react-router-dom";
import Layout from "./_layout";
import Dashboard from "../pages/Dashboard";
import { ProtectedRoute } from "./ProtectedRoute";
import Login from "../pages/Login";
import SignUp from "../pages/SignUp";
const routes: RouteObject[] = [
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/dashboard",
        element: <ProtectedRoute children={<Dashboard />} />,
        children: [],
      },
    ],
  },
  {
    path: "/login",
    element: <Login />,
    children: [],
  },
  {
    path: "/sign-up",
    element: <SignUp />,
    children: [],
  },
];
export const router = createHashRouter(routes);
