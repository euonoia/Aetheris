export interface Detection {
    class_id: number;
    class_name: string;
    confidence: number;
    bounding_box: number[]; // [x1, y1, x2, y2]
}

export interface VehicleStatistics {
    car: number;
    motorcycle: number;
    bus: number;
    truck: number;
}

export interface BaseDetectionResponse {
    filename: string;
    total_vehicle_detections: number;
    vehicle_statistics: VehicleStatistics;
}

export interface ImageDetectionResponse extends BaseDetectionResponse {
    image_url: string;
    detections: Detection[];
}

export interface VideoDetectionResponse extends BaseDetectionResponse {
    video_url: string;
    processing_time: number;
    total_frames: number;
}

export type DetectionResponse = ImageDetectionResponse | VideoDetectionResponse;

export interface VideoTrackingResponse {
    filename: string;
    video_url: string;
    processing_time: number;
    total_frames: number;
    unique_vehicle_count: number;
    tracked_vehicle_ids: number[];
    vehicle_statistics: VehicleStatistics;
}

export interface ActiveTrackDetail {
    track_id: number;
    class_name: string;
    confidence: number;
    bbox: [number, number, number, number];
    first_frame: number;
    last_frame: number;
    total_frames: number;
}

export type TrackingJobStatus = "queued" | "processing" | "completed" | "failed";

export interface TrackVideoJobResponse {
    job_id: string;
}

export interface TrackingStatusResponse {
    job_id: string;
    filename: string;
    status: TrackingJobStatus;
    progress_percentage: number;
    current_frame: number;
    total_frames: number;
    elapsed_processing_time: number;
    processing_fps: number;
    active_tracked_vehicles: number[];
    active_tracked_vehicle_details: ActiveTrackDetail[];
    unique_tracked_vehicle_ids: number[];
    vehicle_statistics: VehicleStatistics;
    video_url: string | null;
    error: string | null;
}

export interface TrackingSocketMessage {
    frame: string;
    frame_number: number;
    processing_fps: number;
    elapsed_time: number;
    active_tracks: ActiveTrackDetail[];
    vehicle_statistics: VehicleStatistics;
    progress: number;
}
