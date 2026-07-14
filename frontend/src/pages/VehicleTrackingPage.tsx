import { useState } from "react";
import VehicleStats from "../components/VehicleStats";
import { useTrackingJob } from "../hooks/useTrackingJob";

function VehicleTrackingPage() {
  const [file, setFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState<number>(0.25);
  const { status, loading, startTracking } = useTrackingJob();

  const handleUpload = async () => {
    if (!file) {
      alert("Select a video first");
      return;
    }

    if (!file.type.startsWith("video/")) {
      alert("Vehicle tracking only supports video files");
      return;
    }

    try {
      await startTracking(file, threshold);
    } catch (error) {
      console.error(error);
      alert("Tracking failed");
    }
  };

  const isComplete = status?.status === "completed";

  return (
    <div>
      <h1>Vehicle Tracking</h1>
      <p style={{ marginTop: 0, color: "#555" }}>
        Upload a video to assign persistent IDs to vehicles using ByteTrack.
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

      <button onClick={handleUpload} disabled={loading || !file}>
        {loading ? "Tracking..." : "Track Vehicles"}
      </button>

      {loading && status && (
        <p style={{ marginTop: "1rem" }}>
          Processing frame {status.current_frame} of {status.total_frames}...
        </p>
      )}

      {isComplete && status.video_url && (
        <div style={{ marginTop: "1.5rem" }}>
          <h2>Tracked Video</h2>
          <video controls width={800} style={{ maxWidth: "100%" }} src={status.video_url} />

          <div style={{ marginTop: "1rem" }}>
            <strong>Total unique vehicles:</strong> {status.unique_tracked_vehicle_ids.length}
            <br />
            <strong>Processing time:</strong> {status.elapsed_processing_time}s
            <br />
            <strong>Total frames:</strong> {status.total_frames}
          </div>

          <h3 style={{ marginTop: "1rem" }}>Tracked Vehicle Statistics</h3>
          <VehicleStats
            stats={status.vehicle_statistics}
            totalLabel="Unique vehicles"
            totalValue={status.unique_tracked_vehicle_ids.length}
          />

          <h3 style={{ marginTop: "1rem" }}>Tracked Vehicle IDs</h3>
          <p style={{ marginTop: 0 }}>
            {status.unique_tracked_vehicle_ids.length > 0
              ? status.unique_tracked_vehicle_ids.join(", ")
              : "No vehicles tracked"}
          </p>
        </div>
      )}

      {status?.status === "failed" && (
        <p style={{ marginTop: "1rem", color: "#b00020" }}>
          Tracking failed: {status.error ?? "Unknown error"}
        </p>
      )}
    </div>
  );
}

export default VehicleTrackingPage;
