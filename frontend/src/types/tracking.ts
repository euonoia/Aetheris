export interface VehicleStatistics {
  car: number;
  motorcycle: number;
  bus: number;
  truck: number;
}

export interface TrackedVehicle {
  track_id: number;
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number];
  first_frame: number;
  last_frame: number;
  total_frames: number;
}
