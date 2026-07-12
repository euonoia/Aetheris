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

export interface DetectionResponse {
    filename: string;
    image_url: string; // annotated image URL
    total_vehicle_detections: number;
    vehicle_statistics: VehicleStatistics;
    detections: Detection[];
}