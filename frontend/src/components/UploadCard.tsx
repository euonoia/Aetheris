import type { CSSProperties } from "react";

interface UploadCardProps {
  file: File | null;
  threshold: number;
  loading: boolean;
  onFileChange: (file: File | null) => void;
  onThresholdChange: (value: number) => void;
  onSubmit: () => void;
}

const cardStyle: CSSProperties = {
  padding: "1.5rem",
  borderRadius: 20,
  background: "rgba(18, 24, 40, 0.95)",
  boxShadow: "0 20px 45px rgba(0,0,0,0.15)",
  border: "1px solid rgba(255,255,255,0.08)",
};

const buttonStyle: CSSProperties = {
  width: "100%",
  marginTop: "1rem",
  padding: "0.95rem 1rem",
  borderRadius: 14,
  border: "none",
  cursor: "pointer",
  color: "#fff",
  background: "#22c55e",
  fontWeight: 700,
};

function UploadCard({ file, threshold, loading, onFileChange, onThresholdChange, onSubmit }: UploadCardProps) {
  return (
    <div style={cardStyle}>
      <h2 style={{ marginTop: 0, color: "#fff" }}>Video Upload</h2>
      <p style={{ color: "#cbd5e1", marginBottom: "1.25rem" }}>
        Upload a CCTV video to monitor vehicles, track IDs, and view annotated output.
      </p>

      <input
        type="file"
        accept="video/*"
        onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        style={{ width: "100%", padding: "0.35rem", borderRadius: 12, border: "1px solid rgba(148,163,184,0.3)", background: "rgba(15,23,42,0.8)", color: "#fff" }}
      />

      <div style={{ marginTop: "1.25rem" }}>
        <label style={{ display: "block", color: "#cbd5e1", marginBottom: "0.5rem" }}>
          Confidence threshold: {threshold.toFixed(2)}
        </label>
        <input
          type="range"
          min={0.25}
          max={1}
          step={0.01}
          value={threshold}
          onChange={(event) => onThresholdChange(Number(event.target.value))}
          style={{ width: "100%" }}
        />
      </div>

      <button type="button" style={buttonStyle} onClick={onSubmit} disabled={loading || !file}>
        {loading ? "Starting monitoring..." : "Start Monitoring"}
      </button>

      {file && (
        <p style={{ marginTop: "1rem", color: "#cbd5e1" }}>
          Selected file: <strong>{file.name}</strong>
        </p>
      )}
    </div>
  );
}

export default UploadCard;
