export type ViolationStatus = "detected" | "under_review" | "citation_issued" | "dismissed";
export type ViolationSeverity = "minor" | "moderate" | "severe";
export type CitationStatus = "pending" | "paid" | "overdue" | "appealed" | "waived";
export type VehicleRisk = "low" | "moderate" | "high" | "blacklisted";
export type UserRole = "admin" | "barangay_captain" | "traffic_officer" | "encoder";
export type FleetStatus = "on_route" | "idle" | "maintenance" | "delayed";

export interface Violation {
  id: string;
  plateNumber: string;
  vehicleType: string;
  vehicleColor: string;
  violationType: string;
  severity: ViolationSeverity;
  status: ViolationStatus;
  location: string;
  cameraId: string;
  timestamp: string;
  confidence: number;
  officerAssigned?: string;
  gps: { lat: number; lng: number };
  evidenceImages: number;
}

export interface Vehicle {
  id: string;
  plateNumber: string;
  type: string;
  make: string;
  model: string;
  color: string;
  ownerName: string;
  ownerAddress: string;
  ownerContact: string;
  registrationExpiry: string;
  risk: VehicleRisk;
  totalViolations: number;
  totalCitations: number;
  outstandingBalance: number;
  blacklisted: boolean;
}

export interface Citation {
  id: string;
  ticketNumber: string;
  plateNumber: string;
  violatorName: string;
  violationType: string;
  amount: number;
  status: CitationStatus;
  dateIssued: string;
  dueDate: string;
  officer: string;
  location: string;
}

export interface SystemUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: "active" | "inactive";
  lastActive: string;
  avatar?: string;
}

export interface TransportRoute {
  id: string;
  code: string;
  name: string;
  vehiclesAssigned: number;
  avgDelay: number;
  status: FleetStatus;
  driver: string;
  demand: "low" | "moderate" | "high";
  nextDeparture: string;
}

export interface IncidentFeedItem {
  id: string;
  type: string;
  location: string;
  timestamp: string;
  severity: ViolationSeverity;
}

export interface NavItem {
  title: string;
  href: string;
  icon: keyof typeof import("lucide-react");
}
