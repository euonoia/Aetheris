import { useRef, useState, type MouseEvent, type ChangeEvent } from "react";
import type { ParkingVideoResponse } from "./types";

const API_BASE = "http://localhost:8000";
const CANVAS_DISPLAY_WIDTH = 640;

interface Point {
  x: number;
  y: number;
}

function ParkingViolation() {
  const [file, setFile] = useState<File | null>(null);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [naturalSize, setNaturalSize] = useState<{ width: number; height: number } | null>(null);
  const [zone, setZone] = useState<Point[]>([]);
  const [dwellSeconds, setDwellSeconds] = useState<number>(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ParkingVideoResponse | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setResult(null);
    setError(null);
    setZone([]);
    setVideoSrc(URL.createObjectURL(selected));
  };

  // Once the video's first frame is ready, paint it onto the canvas so the
  // user has something to click zone points on.
  const handleLoadedData = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    setNaturalSize({ width: video.videoWidth, height: video.videoHeight });

    const displayHeight = (video.videoHeight / video.videoWidth) * CANVAS_DISPLAY_WIDTH;
    canvas.width = CANVAS_DISPLAY_WIDTH;
    canvas.height = displayHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  };

  const handleVideoError = () => {
    setError(
      "This browser couldn't decode that video file. If you're on Linux/Firefox, try Chrome/Chromium, " +
        "or re-encode the clip to H.264 with: ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4"
    );
  };

  const redrawZone = (points: Point[]) => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    if (points.length === 0) return;

    ctx.strokeStyle = "#ffb300";
    ctx.fillStyle = "rgba(255, 179, 0, 0.25)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.slice(1).forEach((p) => ctx.lineTo(p.x, p.y));
    if (points.length > 2) ctx.closePath();
    ctx.stroke();
    if (points.length > 2) ctx.fill();

    points.forEach((p) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#ffb300";
      ctx.fill();
    });
  };

  const handleCanvasClick = (e: MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const point: Point = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    const next = [...zone, point];
    setZone(next);
    redrawZone(next);
  };

  const undoPoint = () => {
    const next = zone.slice(0, -1);
    setZone(next);
    redrawZone(next);
  };

  const clearZone = () => {
    setZone([]);
    redrawZone([]);
  };

  // Map canvas (display) coordinates back to the video's real pixel
  // dimensions, since that's the resolution the backend processes frames at.
  const scaledZone = (): [number, number][] => {
    const canvas = canvasRef.current;
    if (!canvas || !naturalSize) return [];
    const scaleX = naturalSize.width / canvas.width;
    const scaleY = naturalSize.height / canvas.height;
    return zone.map((p) => [p.x * scaleX, p.y * scaleY]);
  };

  const handleSubmit = async () => {
    if (!file) return;
    if (zone.length < 3) {
      setError("Click at least 3 points on the frame to draw the no-parking zone.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("zone", JSON.stringify(scaledZone()));
    formData.append("dwell_seconds", String(dwellSeconds));

    try {
      const res = await fetch(`${API_BASE}/violations/parking/video`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error: ${res.status}`);
      }
      const data: ParkingVideoResponse = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <p className="hint">
        Upload a video, then click 3+ points on the frame below to mark the no-parking zone. A
        vehicle that sits inside the zone, mostly still, for longer than the dwell time is
        flagged as illegal parking.
      </p>

      <input type="file" accept="video/*" onChange={handleFileChange} />

      {videoSrc && (
        <>
          <video
            ref={videoRef}
            src={videoSrc}
            onLoadedData={handleLoadedData}
            onError={handleVideoError}
            muted
            playsInline
            className="source-video"
          />

          <div className="zone-editor">
            <canvas ref={canvasRef} onClick={handleCanvasClick} />
          </div>

          <div className="zone-actions">
            <span>
              {zone.length} point{zone.length === 1 ? "" : "s"}
            </span>
            <button type="button" onClick={undoPoint} disabled={zone.length === 0}>
              Undo point
            </button>
            <button type="button" onClick={clearZone} disabled={zone.length === 0}>
              Clear zone
            </button>
          </div>

          <div className="dwell-input">
            <label htmlFor="dwell">Dwell time before flagging (seconds)</label>
            <input
              id="dwell"
              type="number"
              min={1}
              value={dwellSeconds}
              onChange={(e) => setDwellSeconds(Number(e.target.value))}
            />
          </div>

          <button onClick={handleSubmit} disabled={loading || zone.length < 3}>
            {loading ? "Processing video…" : "Run illegal parking detection"}
          </button>
        </>
      )}

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="results">
          <h3>Annotated video</h3>
          <video controls className="result-video" src={`${API_BASE}${result.video_url}`} />

          <h3>Violations ({result.violations.length})</h3>
          {result.violations.length === 0 ? (
            <p>No illegal parking detected.</p>
          ) : (
            <ul>
              {result.violations.map((v, i) => (
                <li key={i}>
                  <span className="label">
                    {v.class} #{v.track_id}
                  </span>
                  <span>
                    stationary {v.dwell_seconds}s, flagged at {v.timestamp.toFixed(1)}s
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default ParkingViolation;