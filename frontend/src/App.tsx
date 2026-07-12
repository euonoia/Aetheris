import { useState } from "react";
import ObjectDetection from "./ObjectDetection";
import ParkingViolation from "./ParkingViolation";

type Tab = "detection" | "parking";

function App() {
  const [tab, setTab] = useState<Tab>("detection");

  return (
    <div className="app">
      <header>
        <h1>Traffic Violation Detection</h1>
        <p>YOLOv8 + FastAPI backend, React + TypeScript frontend.</p>
      </header>

      <nav className="tabs">
        <button className={tab === "detection" ? "active" : ""} onClick={() => setTab("detection")}>
          Object Detection
        </button>
        <button className={tab === "parking" ? "active" : ""} onClick={() => setTab("parking")}>
          Illegal Parking
        </button>
      </nav>

      {tab === "detection" ? <ObjectDetection /> : <ParkingViolation />}
    </div>
  );
}

export default App;