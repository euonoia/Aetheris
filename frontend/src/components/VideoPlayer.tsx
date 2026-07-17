import type { CSSProperties } from "react";

interface VideoPlayerProps {
  src: string;
}

const videoContainerStyle: CSSProperties = {
  marginTop: "1.5rem",
  borderRadius: 20,
  overflow: "hidden",
  background: "rgba(15, 23, 42, 0.95)",
  border: "1px solid rgba(255,255,255,0.08)",
  boxShadow: "0 20px 45px rgba(0,0,0,0.15)",
};

function VideoPlayer({ src }: VideoPlayerProps) {
  return (
    <div style={videoContainerStyle}>
      <h3 style={{ margin: "1rem 1.5rem 0", color: "#fff" }}>Processed Tracking Video</h3>
      <video controls src={src} style={{ width: "100%", display: "block" }} />
      <div style={{ padding: "1rem 1.5rem 1.5rem", color: "#94a3b8" }}>
        The processed MP4 shows green bounding boxes, vehicle class names, IDs, and confidence.
      </div>
    </div>
  );
}

export default VideoPlayer;
