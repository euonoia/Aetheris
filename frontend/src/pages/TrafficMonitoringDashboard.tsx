import { useState } from "react";
import VehicleStats from "../components/VehicleStats";
import { useTrackingJob } from "../hooks/useTrackingJob";

function TrafficMonitoringDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState<number>(0.25);
  const { status, loading, startTracking } = useTrackingJob();

  const handleStartTracking = async () => {
    if (!file) {
      alert("Select a video first");
      return;
    }

    if (!file.type.startsWith("video/")) {
      alert("Traffic monitoring only supports video files");
      return;
    }

    try {
      await startTracking(file, threshold);
    } catch (error) {
      console.error(error);
      alert("Failed to start tracking job");
    }
  };

  const isProcessing = status?.status === "queued" || status?.status === "processing";

  return (
    <div>
      <h1>Traffic Monitoring Dashboard</h1>
      <p style={{ marginTop: 0, color: "#555" }}>
        Upload a video and watch live tracking progress while the backend processes each frame.
      </p>

      <input
        type="file"
        accept="video/*"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />

      <div style={{ marginTop: "1rem" }}>
        <label>
          Confidence threshold: {threshold.toFixed(2)}
          <br />
          <input
            type="range"
            min={0.25}
            max={1}
            step={0.01}
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            style={{ width: "100%" }}
          />
        </label>
      </div>

      <br />
      <br />

      <button onClick={handleStartTracking} disabled={loading || !file}>
        {loading ? "Monitoring..." : "Start Monitoring"}
      </button>

      {status && (
        <div style={{ marginTop: "1.5rem" }}>
          <h2>Live Processing Status</h2>

          <div style={{ marginBottom: "1rem" }}>
            <strong>Status:</strong> {status.status}
            {status.error && (
              <>
                <br />
                <strong style={{ color: "#b00020" }}>Error:</strong> {status.error}
              </>
            )}
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <strong>Progress:</strong> {status.progress_percentage.toFixed(1)}%
            <div
              style={{
                marginTop: "0.5rem",
                width: "100%",
                maxWidth: 600,
                height: 16,
                backgroundColor: "#eee",
                borderRadius: 8,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${status.progress_percentage}%`,
                  height: "100%",
                  backgroundColor: isProcessing ? "#4caf50" : "#2196f3",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <strong>Frame:</strong> {status.current_frame} / {status.total_frames}
            <br />
            <strong>Processing FPS:</strong> {status.processing_fps}
            <br />
            <strong>Elapsed time:</strong> {status.elapsed_processing_time}s
          </div>

          <h3>Active Tracked IDs (current frame)</h3>
          <p style={{ marginTop: 0 }}>
            {status.active_tracked_vehicles.length > 0
              ? status.active_tracked_vehicles.join(", ")
              : "None"}
          </p>

          <h3>Unique Tracked IDs (entire video)</h3>
          <p style={{ marginTop: 0 }}>
            {status.unique_tracked_vehicle_ids.length > 0
              ? status.unique_tracked_vehicle_ids.join(", ")
              : "None yet"}
          </p>

          <h3>Vehicle Statistics</h3>
          <VehicleStats
            stats={status.vehicle_statistics}
            totalLabel="Unique vehicles"
            totalValue={status.unique_tracked_vehicle_ids.length}
          />

          {status.status === "completed" && status.video_url && (
            <div style={{ marginTop: "1.5rem" }}>
              <h2>Tracked Video</h2>
              <video controls width={800} style={{ maxWidth: "100%" }} src={status.video_url} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default TrafficMonitoringDashboard;
