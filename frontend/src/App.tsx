import { useState } from "react";
import { api } from "./services/api";
import type { DetectionResponse } from "./types/api";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [threshold, setThreshold] = useState<number>(0.25);

  const handleUpload = async () => {
    if (!file) {
      alert("Select a file first");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);
      // send threshold as a form field (backend expects `threshold` in Form)
      formData.append("threshold", String(threshold));

      const response = await api.post<DetectionResponse>("/detect-image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>YOLO Vehicle Detector</h1>

      <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />

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

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {result && (
        <div style={{ marginTop: "1.5rem" }}>
          <h2>Processed Image</h2>
          <img src={result.image_url} alt="Processed upload" width={800} style={{ maxWidth: "100%" }} />

          <h3 style={{ marginTop: "1rem" }}>Detected Vehicles</h3>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
              <strong>Cars</strong>
              <div>{result.vehicle_statistics.car}</div>
            </div>
            <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
              <strong>Motorcycles</strong>
              <div>{result.vehicle_statistics.motorcycle}</div>
            </div>
            <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
              <strong>Buses</strong>
              <div>{result.vehicle_statistics.bus}</div>
            </div>
            <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
              <strong>Trucks</strong>
              <div>{result.vehicle_statistics.truck}</div>
            </div>
            <div style={{ padding: "0.5rem 1rem", border: "1px solid #ddd", borderRadius: 6 }}>
              <strong>Total</strong>
              <div>{result.total_vehicle_detections}</div>
            </div>
          </div>

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
                    <td style={{ border: "1px solid #ddd", padding: "8px" }}>[{d.bounding_box.join(", ")}]</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;