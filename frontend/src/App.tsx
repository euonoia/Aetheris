import { useState } from "react";
import DetectionPage from "./pages/DetectionPage";
import VehicleTrackingPage from "./pages/VehicleTrackingPage";
import MonitoringPage from "./pages/MonitoringPage";

type AppPage = "detect" | "track" | "dashboard";

function App() {
  const [page, setPage] = useState<AppPage>("detect");

  return (
    <div style={{ padding: "2rem" }}>
      <nav style={{ display: "flex", gap: "0.75rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        <button type="button" onClick={() => setPage("detect")} disabled={page === "detect"}>
          Detect Vehicles
        </button>
        <button type="button" onClick={() => setPage("track")} disabled={page === "track"}>
          Track Vehicles
        </button>
        <button type="button" onClick={() => setPage("dashboard")} disabled={page === "dashboard"}>
          Traffic Dashboard
        </button>
      </nav>

      {page === "detect" && <DetectionPage />}
      {page === "track" && <VehicleTrackingPage />}
      {page === "dashboard" && <MonitoringPage />}
    </div>
  );
}

export default App;
