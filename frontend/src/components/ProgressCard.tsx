import type { CSSProperties } from "react";
import type { TrackingStatusResponse } from "../types/api";

interface ProgressCardProps {
  status: TrackingStatusResponse;
}

const cardStyle: CSSProperties = {
  padding: "1.5rem",
  borderRadius: 20,
  background: "rgba(15, 23, 42, 0.95)",
  boxShadow: "0 20px 45px rgba(0,0,0,0.15)",
  border: "1px solid rgba(255,255,255,0.08)",
};

const progressBarContainer: CSSProperties = {
  width: "100%",
  height: 16,
  borderRadius: 12,
  background: "rgba(148,163,184,0.15)",
  overflow: "hidden",
  marginTop: "0.75rem",
};

function ProgressCard({ status }: ProgressCardProps) {
  return (
    <div style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
        <div>
          <h3 style={{ margin: "0 0 0.5rem", color: "#fff" }}>Processing Status</h3>
          <p style={{ margin: 0, color: "#94a3b8" }}>Live tracking progress and telemetry from the backend worker.</p>
        </div>
        <span style={{ color: status.status === "failed" ? "#f87171" : "#34d399", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em" }}>
          {status.status}
        </span>
      </div>

      <div style={progressBarContainer}>
        <div
          style={{
            height: "100%",
            width: `${status.progress_percentage}%`,
            background: "#22c55e",
            transition: "width 0.25s ease",
          }}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: "1rem", marginTop: "1.25rem", color: "#e2e8f0" }}>
        <div>
          <strong>Frame</strong>
          <div>{status.current_frame} / {status.total_frames}</div>
        </div>
        <div>
          <strong>FPS</strong>
          <div>{status.processing_fps}</div>
        </div>
        <div>
          <strong>Elapsed</strong>
          <div>{status.elapsed_processing_time}s</div>
        </div>
        <div>
          <strong>Tracked IDs</strong>
          <div>{status.unique_tracked_vehicle_ids.length}</div>
        </div>
      </div>

      {status.error && (
        <div style={{ marginTop: "1rem", color: "#fda4af", fontWeight: 600 }}>
          Error: {status.error}
        </div>
      )}
    </div>
  );
}

export default ProgressCard;
