import { useMemo, useState } from "react";
import { Camera, CheckCircle2, Crosshair, MapPin, ScanLine, Timer, XCircle, Radio as RadioIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { api } from "../services/api";
import type { DetectionResponse } from "../types/api";
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageHeader } from "@/components/shared/PageHeader";
import { ViolationStatusBadge, SeverityBadge } from "@/components/shared/StatusBadges";
import { violations, cameras } from "@/data/mock-violations";
import { formatDateTime } from "@/lib/utils";
import { toast } from "sonner";

const boxes = [
  { x: 18, y: 30, w: 22, h: 30, label: "Motorcycle", conf: 0.96, violation: true },
  { x: 55, y: 42, w: 26, h: 24, label: "Sedan", conf: 0.91, violation: false },
  { x: 68, y: 20, w: 16, h: 16, label: "Plate: NDX 2291", conf: 0.88, violation: true },
];

export function ViolationRecordingPage() {
  const [camera, setCamera] = useState(cameras[0].id);
  const [selectedId, setSelectedId] = useState(violations[0].id);
  const selected = useMemo(() => violations.find((v) => v.id === selectedId) ?? violations[0], [selectedId]);
  const activeCam = cameras.find((c) => c.id === camera) ?? cameras[0];

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
    <div className="space-y-6">
      <PageHeader
        title="YOLO Vehicle Detector"
        description="Live YOLOv8 detection feed and automated evidence review"
        actions={
          <Select value={camera} onValueChange={(value) => value && setCamera(value)}>
            <SelectTrigger className="w-64"><SelectValue /></SelectTrigger>
            <SelectContent>
              {cameras.map((c) => (
                <SelectItem key={c.id} value={c.id}>{c.id} — {c.location}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        }
      />

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
              {/* simulated night-mode camera texture */}
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

              <div className="absolute left-3 top-3 flex items-center gap-1.5 rounded bg-black/50 px-2 py-1 text-[10px] font-mono text-white">
                <ScanLine className="h-3 w-3" /> YOLOv8n · 24 FPS
              </div>
              <div className="absolute right-3 top-3 rounded bg-black/50 px-2 py-1 text-[10px] font-mono text-white">
                {new Date().toLocaleTimeString("en-PH")}
              </div>
              <div className="absolute bottom-3 left-3 rounded bg-black/50 px-2 py-1 text-[10px] font-mono text-white">
                GPS 14.7449° N, 121.0233° E
              </div>
            </div>

            <div className="mt-4 grid grid-cols-3 gap-3">
              <div className="rounded-md border border-border p-3">
                <p className="text-xs text-muted-foreground">Vehicle Count</p>
                <p className="font-display text-lg font-bold">12</p>
              </div>
              <div className="rounded-md border border-border p-3">
                <p className="text-xs text-muted-foreground">Detections (session)</p>
                <p className="font-display text-lg font-bold">3</p>
              </div>
              <div className="rounded-md border border-border p-3">
                <p className="text-xs text-muted-foreground">Avg. Confidence</p>
                <p className="font-display text-lg font-bold">91.7%</p>
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
                <Button className="uploadBtn" onClick={handleUpload} disabled={loading}>
                    {loading ? "Uploading..." : "Upload"}
                </Button>
            </div>
          </CardContent>
        </Card>

        {/* Detection result panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Crosshair className="h-4 w-4 text-primary" /> Detection Result</CardTitle>
            <CardDescription>Auto-classified from current frame</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border border-accent/30 bg-accent/5 p-3">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-accent">Violation Detected</p>
                <Badge variant="default">Live</Badge>
              </div>
              <p className="mt-1 text-sm font-medium">Illegal Parking — Motorcycle</p>
              <p className="text-xs text-muted-foreground">Plate: NDX 2291 · Detected 00:03 ago</p>
            </div>

            <div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Confidence Score</span>
                <span className="font-semibold">96%</span>
              </div>
              <Progress value={96} className="mt-1.5 h-1.5" />
            </div>

            <Separator />

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Vehicle Type</span><span className="font-medium">Motorcycle</span></div>
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Color</span><span className="font-medium">Black</span></div>
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Camera</span><span className="font-medium">{activeCam.id}</span></div>
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Timestamp</span><span className="font-medium">{new Date().toLocaleTimeString("en-PH")}</span></div>
            </div>

            <Separator />

            <div className="flex gap-2">
              <Button className="flex-1" onClick={() => toast.success("Citation generated for NDX 2291")}>
                <CheckCircle2 className="h-4 w-4" /> Generate Citation
              </Button>
              <Button variant="outline" size="icon" onClick={() => toast("Detection dismissed")}>
                <XCircle className="h-4 w-4" />
              </Button>
            </div>
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
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
