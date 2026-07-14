import type { Violation } from "@/types";

export const violationTypes = [
  "Illegal Parking", "No Helmet", "Beating the Red Light", "Counter-flow",
  "Obstruction", "No Plate Number", "Overloading", "Illegal Terminal", "Colorum Vehicle", "Swerving",
];

export const cameras = [
  { id: "CAM-178-01", location: "Camarin Rd. corner Zabarte Rd." },
  { id: "CAM-178-02", location: "Camarin Rd. corner Sampaguita St." },
  { id: "CAM-178-03", location: "Gregorio Araneta Ave. Junction" },
  { id: "CAM-178-04", location: "Brgy. 178 Covered Court Front" },
  { id: "CAM-178-05", location: "Camarin Public Market Access Rd." },
  { id: "CAM-178-06", location: "Zabarte Rd. corner Llano St." },
];

function rand<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

const plates = ["NDX 2291", "ABC 1029", "TYU 7734", "WQR 4482", "LKJ 9021", "ZXC 5567", "MNB 3310", "POI 8845", "GHT 1123", "VBN 6690"];
const vehicleTypes = ["Motorcycle", "Sedan", "Tricycle", "Jeepney", "Van", "SUV", "Multicab"];
const colors = ["Black", "White", "Red", "Silver", "Blue", "Gray"];
const officers = ["PO2 Marasigan", "PO1 Delos Santos", "SPO1 Villareal", "PO3 Cabrera", "Traffic Aide Reyes"];

export const violations: Violation[] = Array.from({ length: 28 }).map((_, i) => {
  const cam = rand(cameras);
  const statusRoll = Math.random();
  const status = statusRoll > 0.75 ? "citation_issued" : statusRoll > 0.5 ? "under_review" : statusRoll > 0.1 ? "detected" : "dismissed";
  return {
    id: `VIO-${(1000 + i).toString()}`,
    plateNumber: rand(plates),
    vehicleType: rand(vehicleTypes),
    vehicleColor: rand(colors),
    violationType: rand(violationTypes),
    severity: rand(["minor", "moderate", "severe"]) as Violation["severity"],
    status: status as Violation["status"],
    location: cam.location,
    cameraId: cam.id,
    timestamp: new Date(Date.now() - i * 1000 * 60 * (17 + Math.random() * 40)).toISOString(),
    confidence: Math.round((0.82 + Math.random() * 0.17) * 100) / 100,
    officerAssigned: status !== "detected" ? rand(officers) : undefined,
    gps: { lat: 14.7449 + (Math.random() - 0.5) * 0.01, lng: 121.0233 + (Math.random() - 0.5) * 0.01 },
    evidenceImages: 2 + Math.floor(Math.random() * 3),
  };
});

export const topViolationLocations = [
  { location: "Camarin Rd. corner Zabarte Rd.", count: 41 },
  { location: "Gregorio Araneta Ave. Junction", count: 33 },
  { location: "Camarin Public Market Access Rd.", count: 27 },
  { location: "Zabarte Rd. corner Llano St.", count: 19 },
  { location: "Brgy. 178 Covered Court Front", count: 12 },
];

export const monthlyViolationTrend = [
  { month: "Feb", violations: 210, citations: 152 },
  { month: "Mar", violations: 244, citations: 189 },
  { month: "Apr", violations: 198, citations: 160 },
  { month: "May", violations: 267, citations: 205 },
  { month: "Jun", violations: 231, citations: 178 },
  { month: "Jul", violations: 189, citations: 141 },
];

export const violationsByType = violationTypes.map((t) => ({
  type: t,
  count: 8 + Math.floor(Math.random() * 55),
}));
