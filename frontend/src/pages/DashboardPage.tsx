import { useMemo, useState } from "react";
import { Camera, CheckCircle2, Crosshair, MapPin, ScanLine, Timer, XCircle, Radio as RadioIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider"
import { ViolationStatusBadge, SeverityBadge } from "@/components/shared/StatusBadges";
import { violations, cameras } from "@/data/mock-violations";
import { formatDateTime } from "@/lib/utils";
import { toast } from "sonner";
import { useTrackingJob } from "../hooks/useTrackingJob";
import { useTrackingSocket } from "../hooks/useTrackingSocket";
import type { TrackedVehicle } from "../types/tracking";
import type { TrackingStatusResponse } from "../types/api";
import type { TrackingJobStatus } from "../types/api";
import LiveFramePreview from "#components/LiveFramePreview";

const boxes = [
  { x: 18, y: 30, w: 22, h: 30, label: "Motorcycle", conf: 0.96, violation: true },
  { x: 55, y: 42, w: 26, h: 24, label: "Sedan", conf: 0.91, violation: false },
  { x: 68, y: 20, w: 16, h: 16, label: "Plate: NDX 2291", conf: 0.88, violation: true },
];

export default function DashboardPage() {
    const [camera, setCamera] = useState(cameras[0].id);
    const [selectedId, setSelectedId] = useState(violations[0].id);
    const selected = useMemo(() => violations.find((v) => v.id === selectedId) ?? violations[0], [selectedId]);
    const activeCam = cameras.find((c) => c.id === camera) ?? cameras[0];

    const [file, setFile] = useState<File | null>(null);
    const [threshold, setThreshold] = useState<number>(0.25);
    const { status, loading, jobId, startTracking } = useTrackingJob();
    const { message, connectionState } = useTrackingSocket(jobId);

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

    type progressVariantType = Record<TrackingJobStatus, "default" | "secondary" | "destructive" | "outline">;
    const progressVariantBadge: progressVariantType = {
        "queued" : "outline",
        "processing" : "secondary",
        "completed" : "default",
        "failed" : "destructive"
    } 

  return (
    <div className="space-y-6">
      
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {/* Live camera + detection overlay */}
        <Card className="xl:col-span-2">
          <CardHeader className="flex flex-row items-start justify-between gap-3 space-y-0">
            <div className="min-w-0">
              <CardTitle className="flex items-center gap-2">
                <RadioIcon className="h-4 w-4 text-destructive animate-pulse" /> Live Feed — {activeCam.id}
              </CardTitle>
              <CardDescription>{activeCam.location}</CardDescription>
            </div>
            <Badge variant="destructive" className="flex shrink-0 items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-current" /> REC
            </Badge>
          </CardHeader>
          <CardContent>
                <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-[#0d130d]">
               
                    {!message ? loading ? (<h3 className="text-white">loading...</h3>) : (
                    <>
                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(76,175,107,0.12),transparent_45%),radial-gradient(circle_at_75%_70%,rgba(255,153,85,0.10),transparent_40%)]" />
                        <div className="absolute inset-0 bg-grid opacity-10" />

                        {boxes.map((b, i) => (
                            <div
                                key={i}
                                className={`absolute rounded-sm border-2 ${b.violation ? "border-accent" : "border-primary"}`}
                                style={{ left: `${b.x}%`, top: `${b.y}%`, width: `${b.w}%`, height: `${b.h}%` }}
                            >
                            <span
                                className={`absolute -top-6 left-0 whitespace-nowrap rounded px-1.5 py-0.5 text-[10px] font-semibold text-white ${b.violation ? "bg-accent" : "bg-primary"}`}
                            >
                                {b.label} · {Math.round(b.conf * 100)}%
                            </span>
                            </div>
                        ))}
                    
                    </>) : (
                        <LiveFramePreview message={message} />
                    )}

                <div className="absolute left-3 top-3 flex items-center gap-1.5 rounded bg-black/50 px-2 py-1 text-[10px] font-mono text-white">
                    <ScanLine className="h-3 w-3" /> YOLOv8n · {displayFps ?? 0} FPS
                </div>
                <div className="absolute right-3 top-3 rounded bg-black/50 px-2 py-1 text-[10px] font-mono text-white">
                    {new Date().toLocaleTimeString("en-PH")}
                </div>
                <div className="absolute bottom-3 left-3 rounded bg-black/50 px-2 py-1 text-[10px] font-mono text-white">
                    Elapsed time {displayElapsed}s
                </div>
                </div>
              
            <div className="mt-4 grid grid-cols-3 gap-3">
              <div className="rounded-md border border-border p-3">
                <p className="text-xs text-muted-foreground">Cars</p>
                <p className="font-display text-lg font-bold">{summaryStats.car}</p>
              </div>
              <div className="rounded-md border border-border p-3">
                <p className="text-xs text-muted-foreground">Motorcycles</p>
                <p className="font-display text-lg font-bold">{summaryStats.motorcycle}</p>
              </div>
              <div className="rounded-md border border-border p-3">
                <p className="text-xs text-muted-foreground">Buses</p>
                <p className="font-display text-lg font-bold">{summaryStats.bus}</p>
              </div>
              <div className="rounded-md border border-border p-3">
                <p className="text-xs text-muted-foreground">Trucks</p>
                <p className="font-display text-lg font-bold">{summaryStats.truck}</p>
              </div>
              <div className="rounded-md border border-border p-3">
                <p className="text-xs text-muted-foreground">Unique Vehicles</p>
                <p className="font-display text-lg font-bold">{status?.unique_tracked_vehicle_ids.length ?? 0}</p>
              </div>
            </div>
            <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-end">
              <div className="min-w-0 flex-1">
                <label className="mb-2 block text-sm font-medium text-foreground">
                    Confidence threshold: {threshold.toFixed(2)}
                </label>
                <Slider
                    value={threshold}
                    min={0.25}
                    max={1}
                    step={0.01}
                    className="w-full"
                    onValueChange={(value) => setThreshold(Array.isArray(value) ? value[0] : value)}
                />
              </div>
                <label className="border-1 p-2 rounded-md bg-background shadow-xs hover:bg-muted hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground dark:border-input dark:bg-input/30 dark:hover:bg-input/50">
                        <span>{file ? file.name : "Choose file"}</span>
                        <input
                            type="file"
                            className="sr-only"
                            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                        />
                </label>
                <Button className="uploadBtn" onClick={handleStart} disabled={loading}>
                    {loading ? "Starting..." : "Start Tracking"}
                </Button>
            </div>
          </CardContent>
        </Card>

        {/* Detection result panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Crosshair className="h-4 w-4 text-primary" />Current Active Tracks</CardTitle>
            <CardDescription>Live tracking progress and telemetry</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border gap-2 border-accent/30 bg-accent/5 p-3">
                <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-accent">Processing Status</p>
                    <Badge variant={progressVariantBadge[inferredStatus?.status || "default"]}>
                        {inferredStatus?.status}
                    </Badge>
                </div>
                <Progress value={parseFloat(inferredStatus?.progress_percentage.toFixed(1) || "0")} className="mt-4 mb-2 h-1.5" />
                <p className="text-xs flex justify-between text-muted-foreground">
                    <p>Live tracking progress</p>
                    <span className="font-semibold">{inferredStatus?.progress_percentage.toFixed(1)}%</span>
                </p>
            </div>
            <Separator />

            {activeTrackDetails.length === 0 ? (
                <p style={{ color: "#94a3b8", margin: 0 }}>No active tracks detected on the latest frame.</p>
            ) : (
                <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", color: "#060a0f" }}>
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
                    {activeTrackDetails.slice(0, 10).map((track) => (
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
          </CardContent>
        </Card>
      </div>

      {/* Evidence & queue */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Officer Review Queue</CardTitle>
            <CardDescription>Detections awaiting verification, select to inspect evidence</CardDescription>
          </CardHeader>
          <CardContent className="space-y-1">
            {violations.slice(0, 8).map((v) => (
              <button
                key={v.id}
                onClick={() => setSelectedId(v.id)}
                className={`flex w-full items-center gap-3 rounded-md px-2 py-2.5 text-left transition-colors ${selectedId === v.id ? "bg-primary/20" : "hover:bg-secondary/60"}`}
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-secondary">
                  <Camera className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{v.violationType} — {v.plateNumber}</p>
                  <p className="truncate text-xs text-muted-foreground flex items-center gap-1">
                    <MapPin className="h-3 w-3" /> {v.location}
                  </p>
                </div>
                <SeverityBadge severity={v.severity} />
                <ViolationStatusBadge status={v.status} />
              </button>
            ))}
          </CardContent>
        </Card>

        {/* Automatic Evidence Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Automatic Evidence Panel</CardTitle>
            <CardDescription>{selected.id}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-2">
              {Array.from({ length: selected.evidenceImages }).map((_, i) => (
                <div key={i} className="relative flex aspect-video items-center justify-center rounded-md border border-border bg-primary/10">
                  <Camera className="h-5 w-5 text-muted-foreground" />
                  <span className="absolute bottom-1 right-1 rounded bg-black/60 px-1 text-[9px] text-white">EVID-{i + 1}</span>
                </div>
              ))}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between"><span className="text-muted-foreground">GPS Coordinates</span><span className="font-mono text-xs">{selected.gps.lat.toFixed(4)}, {selected.gps.lng.toFixed(4)}</span></div>
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Camera ID</span><span className="font-medium">{selected.cameraId}</span></div>
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Plate Number</span><span className="font-medium">{selected.plateNumber}</span></div>
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Confidence</span><span className="font-medium">{Math.round(selected.confidence * 100)}%</span></div>
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Evidence Status</span><ViolationStatusBadge status={selected.status} /></div>
            </div>
            <Separator />
            <div>
              <p className="mb-2 text-xs font-semibold text-muted-foreground flex items-center gap-1"><Timer className="h-3.5 w-3.5" /> Evidence Timeline</p>
              <ol className="space-y-2 border-l border-border pl-4 text-xs">
                <li className="relative"><span className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-primary" />Captured at {formatDateTime(selected.timestamp)}</li>
                <li className="relative"><span className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-accent" />Auto-classified by YOLOv8 · {Math.round(selected.confidence * 100)}% conf.</li>
                <li className="relative"><span className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-muted-foreground" />
                  {selected.officerAssigned ? `Assigned to ${selected.officerAssigned}` : "Awaiting officer assignment"}
                </li>
              </ol>
              
            </div>
            <Button className="flex-1" onClick={() => toast.success("Citation generated for NDX 2291")}>
                <CheckCircle2 className="h-4 w-4" /> Generate Citation
            </Button>
          </CardContent>
            
        </Card>
      </div>
    </div>
  );
}
