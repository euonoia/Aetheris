import type { CSSProperties } from "react";
import type { TrackingSocketMessage } from "../types/api";

interface LiveFramePreviewProps {
  message: TrackingSocketMessage | null;
}

const containerStyle: CSSProperties = {
  padding: "1.5rem",
  borderRadius: 20,
  background: "rgba(15, 23, 42, 0.95)",
  border: "1px solid rgba(255,255,255,0.08)",
  boxShadow: "0 20px 45px rgba(0,0,0,0.15)",
};

const frameStyle: CSSProperties = {
  width: "100%",
  height: "auto",
  borderRadius: 16,
  background: "#111827",
  objectFit: "contain",
};

function LiveFramePreview({ message }: LiveFramePreviewProps) {
  if (!message) {
    return (
      <div style={containerStyle}>
        <h3 style={{ marginTop: 0, color: "#fff" }}>Live Monitor</h3>
        <div style={{ color: "#94a3b8" }}>Waiting for live frame updates from the backend.</div>
      </div>
    );
  }

  const src = `data:image/jpeg;base64,${message.frame}`;

  return (
    <div style={containerStyle}>
      <h3 style={{ marginTop: 0, color: "#fff" }}>Live Monitor</h3>
      <img src={src} alt="Live annotated frame" style={frameStyle} />
    </div>
  );
}

export default LiveFramePreview;
