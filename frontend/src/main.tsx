import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "react-datepicker/dist/react-datepicker.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import "./styles/tailwind.output.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
      <App />
  </StrictMode>,
);
