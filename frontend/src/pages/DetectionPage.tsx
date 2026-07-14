import { useState } from "react";
import { detectImage, detectVideo } from "../services/api";
import VehicleStats from "../components/VehicleStats";
import type { DetectionResponse } from "../types/api";

function DetectionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [threshold, setThreshold] = useState<number>(0.25);

  const isVideoFile = (value: File) => value.type.startsWith("video/");

  const handleUpload = async () => {
    if (!file) {
      alert("Select a file first");
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const response = isVideoFile(file)
        ? await detectVideo(file, threshold)
        : await detectImage(file, threshold);

      setResult(response.data as DetectionResponse);
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Vehicle Detection</h1>
      <p style={{ marginTop: 0, color: "#555" }}>
        Upload an image or video to run frame-by-frame vehicle detection.
      </p>

      <input
        type="file"
        accept="image/*,video/*"
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
        {loading ? "Processing..." : "Upload"}
      </button>

      {result && (
        <div style={{ marginTop: "1.5rem" }}>
          {"image_url" in result ? (
            <>
              <h2>Processed Image</h2>
              <img src={result.image_url} alt="Processed upload" width={800} style={{ maxWidth: "100%" }} />
            </>
          ) : (
            <>
              <h2>Processed Video</h2>
              <video controls width={800} style={{ maxWidth: "100%" }} src={result.video_url} />
              <div style={{ marginTop: "1rem" }}>
                <strong>Processing time:</strong> {result.processing_time}s
                <br />
                <strong>Total frames:</strong> {result.total_frames}
              </div>
            </>
          )}

          <h3 style={{ marginTop: "1rem" }}>Detected Vehicles</h3>
          <VehicleStats
            stats={result.vehicle_statistics}
            totalLabel="Total detections"
            totalValue={result.total_vehicle_detections}
          />

          {"detections" in result && result.detections && (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={{ border: "1px solid #ddd", padding: "8px", textAlign: "left" }}>Class ID</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px", textAlign: "left" }}>Class Name</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px", textAlign: "left" }}>Confidence</th>
                    <th style={{ border: "1px solid #ddd", padding: "8px", textAlign: "left" }}>Bounding Box</th>
                  </tr>
                </thead>
                <tbody>
                  {result.detections.map((d, idx) => (
                    <tr key={idx}>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>{d.class_id}</td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>{d.class_name}</td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>{d.confidence.toFixed(2)}</td>
                      <td style={{ border: "1px solid #ddd", padding: "8px" }}>[{d.bounding_box.join(", ")} ]</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DetectionPage;
