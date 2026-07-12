export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class: string;
  confidence: number;
  box: BoundingBox;
}

export interface ImageSize {
  width: number;
  height: number;
}

export interface PredictResponse {
  detections: Detection[];
  annotated_image: string;
  image_size: ImageSize;
}

export interface ParkingViolationEvent {
  track_id: number;
  class: string;
  dwell_seconds: number;
  center: [number, number];
  timestamp: number;
  frame: number;
}

export interface ParkingVideoResponse {
  job_id: string;
  violations: ParkingViolationEvent[];
  video_url: string;
  fps: number;
  frame_count: number;
}