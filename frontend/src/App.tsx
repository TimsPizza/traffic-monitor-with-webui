import "./styles/tailwind.output.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { useState } from "react";
import { RouterProvider } from "react-router-dom";
import { router } from "./routes";

function App() {
  return (
    <>
      <RouterProvider router={router} />
    </>
  );
}

export default App;
