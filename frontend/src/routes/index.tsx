import { createHashRouter, RouteObject } from "react-router-dom";
import Layout from "./_layout";
import Dashboard from "../pages/Dashboard";
import { ProtectedRoute } from "./ProtectedRoute";
import Login from "../pages/Login";
import SignUp from "../pages/SignUp";
import Analytics from "../pages/Analytics";
const routes: RouteObject[] = [
  {
    path: "/",
    element: <ProtectedRoute children={<Layout />} />,
    children: [
      {
        path: "/dashboard",
        element: <ProtectedRoute children={<Dashboard />} />,
        children: [],
      },{
        path: "/analytics",
        element: <ProtectedRoute children={<Analytics />} />,
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
