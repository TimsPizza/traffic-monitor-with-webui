import "bootstrap/dist/css/bootstrap.min.css";
import "./styles/tailwind.output.css";
import { createContext, useEffect, useState } from "react";
import { RouterProvider } from "react-router-dom";
import { router } from "./routes";
import { EMediaBreakpoints } from "./client/types";

interface IWindowSizeContext {
  breakpoint: EMediaBreakpoints;
}

const WindowSizeContext: React.Context<IWindowSizeContext> =
  createContext<IWindowSizeContext>({
    breakpoint: EMediaBreakpoints.lg,
  });

const App = () => {
  const [mediaBreakPoint, setMediaBreakPoint] = useState<EMediaBreakpoints>(
    EMediaBreakpoints.lg,
  );
  useEffect(() => {
    const resizeHandler = () => {
      if (window.innerWidth < 576) {
        setMediaBreakPoint(EMediaBreakpoints.sm);
      } else if (window.innerWidth < 768) {
        setMediaBreakPoint(EMediaBreakpoints.md);
      } else if (window.innerWidth < 992) {
        setMediaBreakPoint(EMediaBreakpoints.lg);
      } else if (window.innerWidth < 1200) {
        setMediaBreakPoint(EMediaBreakpoints.xl);
      } else {
        setMediaBreakPoint(EMediaBreakpoints.xxl);
      }
    };
    window.addEventListener("resize", resizeHandler);
    return () => {
      window.removeEventListener("resize", resizeHandler);
    };
  }, []);
  return (
    <>
      <WindowSizeContext.Provider
        value={{
          breakpoint: mediaBreakPoint,
        }}
      >
        <RouterProvider router={router} />
      </WindowSizeContext.Provider>
    </>
  );
};

export default App;
