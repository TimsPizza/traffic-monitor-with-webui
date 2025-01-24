import { createContext, useEffect, useState } from "react";
import { RouterProvider } from "react-router-dom";
import { router } from "./routes";
import { EMediaBreakpoints } from "./client/types";
import { ToastContainer } from "react-bootstrap";
import { QueryClient, QueryClientProvider } from "react-query";

interface IWindowSizeContext {
  breakpoint: EMediaBreakpoints;
}

export const WindowSizeContext: React.Context<IWindowSizeContext> =
  createContext<IWindowSizeContext>({
    breakpoint: EMediaBreakpoints.lg,
  });

const App = () => {
  const [mediaBreakPoint, setMediaBreakPoint] = useState<EMediaBreakpoints>(
    EMediaBreakpoints.lg,
  );
  const queryClient = new QueryClient();

  useEffect(() => {
    const layoutElement = document.getElementById("layout");
    if (!layoutElement) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        if (width < EMediaBreakpoints.sm) {
          setMediaBreakPoint(EMediaBreakpoints.sm);
        } else if (width < EMediaBreakpoints.md) {
          setMediaBreakPoint(EMediaBreakpoints.md);
        } else if (width < EMediaBreakpoints.lg) {
          setMediaBreakPoint(EMediaBreakpoints.lg);
        } else if (width < EMediaBreakpoints.xl) {
          setMediaBreakPoint(EMediaBreakpoints.xl);
        } else if (width < EMediaBreakpoints.xxl) {
          setMediaBreakPoint(EMediaBreakpoints.xxl);
        }
      }
    });

    resizeObserver.observe(layoutElement);
    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  return (
    <WindowSizeContext.Provider
      value={{
        breakpoint: mediaBreakPoint,
      }}
    >
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <ToastContainer position="top-center" />
      </QueryClientProvider>
    </WindowSizeContext.Provider>
  );
};

export default App;
