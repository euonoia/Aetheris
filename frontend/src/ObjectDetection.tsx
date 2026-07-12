import { useState, type ChangeEvent } from "react";
import type { PredictResponse } from "./types";

const API_URL = "http://localhost:8000/predict";

function ObjectDetection() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(API_URL, { method: "POST", body: formData });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error: ${res.status}`);
      }
      const data: PredictResponse = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <p className="hint">Upload an image and run it through the FastAPI + Ultralytics backend.</p>

      <section className="controls">
        <label className="file-input">
          <input type="file" accept="image/*" onChange={handleFileChange} />
          Choose image
        </label>
        <button onClick={handleSubmit} disabled={!file || loading}>
          {loading ? "Detecting…" : "Detect objects"}
        </button>
      </section>

      {error && <p className="error">{error}</p>}

      <section className="images">
        {preview && (
          <div className="image-card">
            <h3>Original</h3>
            <img src={preview} alt="Uploaded preview" />
          </div>
        )}
        {result && (
          <div className="image-card">
            <h3>Detected</h3>
            <img src={result.annotated_image} alt="Annotated result" />
          </div>
        )}
      </section>

      {result && (
        <section className="detections">
          <h3>Detections ({result.detections.length})</h3>
          {result.detections.length === 0 ? (
            <p>No objects found above the confidence threshold.</p>
          ) : (
            <ul>
              {result.detections.map((d, i) => (
                <li key={i}>
                  <span className="label">{d.class}</span>
                  <span className="confidence">{(d.confidence * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}

export default ObjectDetection;