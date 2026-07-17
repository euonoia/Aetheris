import { useState } from "react";
import { useTrackingJob } from "../hooks/useTrackingJob";
import { useTrackingSocket } from "../hooks/useTrackingSocket";
import UploadCard from "../components/UploadCard";
import ProgressCard from "../components/ProgressCard";
import VehicleStats from "../components/VehicleStats";
import ActiveTracks from "../components/ActiveTracks";
import LiveFramePreview from "../components/LiveFramePreview";
import VideoPlayer from "../components/VideoPlayer";
import type { TrackedVehicle } from "../types/tracking";
import type { TrackingStatusResponse } from "../types/api";

function MonitoringPage() {
  const [file, setFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState<number>(0.25);
  const { status, loading, jobId, startTracking } = useTrackingJob();
  const { message, connectionState } = useTrackingSocket(jobId);

  const handleStart = async () => {
    if (!file) {
      alert("Select a video first");
      return;
    }

    if (!file.type.startsWith("video/")) {
      alert("Traffic monitoring only supports video files");
      return;
    }

    await startTracking(file, threshold);
  };

  const activeTrackDetails: TrackedVehicle[] =
    message?.active_tracks?.map((track) => ({
      track_id: track.track_id,
      class_name: track.class_name,
      confidence: track.confidence,
      bbox: track.bbox,
      first_frame: track.first_frame,
      last_frame: track.last_frame,
      total_frames: track.total_frames,
    })) ??
    status?.active_tracked_vehicle_details?.map((detail) => ({
      track_id: detail.track_id,
      class_name: detail.class_name,
      confidence: detail.confidence,
      bbox: detail.bbox,
      first_frame: detail.first_frame,
      last_frame: detail.last_frame,
      total_frames: detail.total_frames,
    })) ?? [];

  const summaryStats = status?.vehicle_statistics ?? { car: 0, motorcycle: 0, bus: 0, truck: 0 };
  const displayProgress = message?.progress ?? status?.progress_percentage ?? 0;
  const displayFrame = message?.frame_number ?? status?.current_frame ?? 0;
  const displayFps = message?.processing_fps ?? status?.processing_fps ?? 0;
  const displayElapsed = message?.elapsed_time ?? status?.elapsed_processing_time ?? 0;

  const fallbackStatus: TrackingStatusResponse = {
    job_id: jobId ?? "",
    filename: "",
    status: "queued",
    progress_percentage: displayProgress,
    current_frame: displayFrame,
    total_frames: 0,
    elapsed_processing_time: displayElapsed,
    processing_fps: displayFps,
    active_tracked_vehicles: activeTrackDetails.map((track) => track.track_id),
    active_tracked_vehicle_details: activeTrackDetails,
    unique_tracked_vehicle_ids: [],
    vehicle_statistics: summaryStats,
    video_url: null,
    error: null,
  };

  const inferredStatus: TrackingStatusResponse = status ?? fallbackStatus;

  return (
    <div style={{ display: "grid", gap: "1.5rem", padding: "1rem 0" }}>
      <div style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "1fr 1.4fr" }}>
        <UploadCard
          file={file}
          threshold={threshold}
          loading={loading}
          onFileChange={setFile}
          onThresholdChange={setThreshold}
          onSubmit={handleStart}
        />

        <ProgressCard status={inferredStatus} />
      </div>

      <LiveFramePreview message={message} />

      <div style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "1fr 1fr" }}>
        <div style={{ padding: "1.5rem", borderRadius: 20, background: "rgba(15,23,42,0.95)", border: "1px solid rgba(255,255,255,0.08)", boxShadow: "0 20px 45px rgba(0,0,0,0.15)" }}>
          <h3 style={{ marginTop: 0, color: "#fff" }}>Vehicle Statistics</h3>
          <VehicleStats
            stats={summaryStats}
            totalLabel="Unique vehicles"
            totalValue={status?.unique_tracked_vehicle_ids.length ?? 0}
          />
          <div style={{ marginTop: "1rem", color: "#94a3b8" }}>
            <div><strong>Current frame:</strong> {displayFrame}</div>
            <div><strong>Progress:</strong> {displayProgress.toFixed(1)}%</div>
            <div><strong>Processing FPS:</strong> {displayFps}</div>
            <div><strong>Elapsed time:</strong> {displayElapsed}s</div>
            <div><strong>Connection:</strong> {connectionState}</div>
          </div>
        </div>

        <ActiveTracks tracks={activeTrackDetails} />
      </div>

      {status?.status === "completed" && status.video_url && <VideoPlayer src={status.video_url} />}
    </div>
  );
}

export default MonitoringPage;
