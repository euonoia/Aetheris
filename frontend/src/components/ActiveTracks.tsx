import type { CSSProperties } from "react";
import type { TrackedVehicle } from "../types/tracking";

interface ActiveTracksProps {
  tracks: TrackedVehicle[];
}

const cardStyle: CSSProperties = {
  padding: "1.5rem",
  borderRadius: 20,
  background: "rgba(15, 23, 42, 0.95)",
  boxShadow: "0 20px 45px rgba(0,0,0,0.15)",
  border: "1px solid rgba(255,255,255,0.08)",
};

function ActiveTracks({ tracks }: ActiveTracksProps) {
  return (
    <div style={cardStyle}>
      <h3 style={{ margin: "0 0 1rem", color: "#fff" }}>Current Active Tracks</h3>

      {tracks.length === 0 ? (
        <p style={{ color: "#94a3b8", margin: 0 }}>No active tracks detected on the latest frame.</p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", color: "#e2e8f0" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", padding: "0.75rem 0", borderBottom: "1px solid rgba(148,163,184,0.2)" }}>Track ID</th>
                <th style={{ textAlign: "left", padding: "0.75rem 0", borderBottom: "1px solid rgba(148,163,184,0.2)" }}>Type</th>
                <th style={{ textAlign: "left", padding: "0.75rem 0", borderBottom: "1px solid rgba(148,163,184,0.2)" }}>Confidence</th>
                <th style={{ textAlign: "left", padding: "0.75rem 0", borderBottom: "1px solid rgba(148,163,184,0.2)" }}>Last Frame</th>
                <th style={{ textAlign: "left", padding: "0.75rem 0", borderBottom: "1px solid rgba(148,163,184,0.2)" }}>Duration</th>
              </tr>
            </thead>
            <tbody>
              {tracks.slice(0, 10).map((track) => (
                <tr key={track.track_id}>
                  <td style={{ padding: "0.75rem 0" }}>{track.track_id}</td>
                  <td style={{ padding: "0.75rem 0", textTransform: "capitalize" }}>{track.class_name}</td>
                  <td style={{ padding: "0.75rem 0" }}>{track.confidence.toFixed(2)}</td>
                  <td style={{ padding: "0.75rem 0" }}>{track.last_frame}</td>
                  <td style={{ padding: "0.75rem 0" }}>{track.total_frames}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ActiveTracks;
