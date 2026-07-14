import { Badge } from "@/components/ui/badge";
import type { ViolationStatus, CitationStatus, VehicleRisk, ViolationSeverity, FleetStatus } from "@/types";

export function ViolationStatusBadge({ status }: { status: ViolationStatus }) {
    const map: Record<ViolationStatus, { label: string; variant: "default" | "secondary" | "destructive" | "outline" | "link" | "ghost" }> = {
        detected: { label: "Detected", variant: "outline" },
        under_review: { label: "Under Review", variant: "outline" },
        citation_issued: { label: "Citation Issued", variant: "default" },
        dismissed: { label: "Dismissed", variant: "secondary" },
    };
    const m = map[status];
    return <Badge variant={m.variant}>{m.label}</Badge>;
}

export function CitationStatusBadge({ status }: { status: CitationStatus }) {
    const map: Record<CitationStatus, { label: string; variant: "default" | "secondary" | "destructive" | "outline" | "link" | "ghost" }> = {
        pending: { label: "Pending", variant: "outline" },
        paid: { label: "Paid", variant: "default" },
        overdue: { label: "Overdue", variant: "destructive" },
        appealed: { label: "Appealed", variant: "outline" },
        waived: { label: "Waived", variant: "secondary" },
    };
    const m = map[status];
    return <Badge variant={m.variant}>{m.label}</Badge>;
}

export function RiskBadge({ risk }: { risk: VehicleRisk }) {
    const map: Record<VehicleRisk, { label: string; variant: "default" | "secondary" | "destructive" | "outline" | "link" | "ghost" }> = {
        low: { label: "Low Risk", variant: "default" },
        moderate: { label: "Moderate Risk", variant: "outline" },
        high: { label: "High Risk", variant: "destructive" },
        blacklisted: { label: "Blacklisted", variant: "destructive" },
    };
    const m = map[risk];
    return <Badge variant={m.variant}>{m.label}</Badge>;
}

export function SeverityBadge({ severity }: { severity: ViolationSeverity }) {
    const map: Record<ViolationSeverity, { label: string; variant: "default" | "secondary" | "destructive" | "outline" | "link" | "ghost" }> = {
        minor: { label: "Minor", variant: "secondary" },
        moderate: { label: "Moderate", variant: "outline" },
        severe: { label: "Severe", variant: "destructive" },
    };
    const m = map[severity];
    return <Badge variant={m.variant}>{m.label}</Badge>;
}

export function FleetStatusBadge({ status }: { status: FleetStatus }) {
    const map: Record<FleetStatus, { label: string; variant: "default" | "secondary" | "destructive" | "outline" | "link" | "ghost" }> = {
        on_route: { label: "On Route", variant: "default" },
        idle: { label: "Idle", variant: "secondary" },
        maintenance: { label: "Maintenance", variant: "outline" },
        delayed: { label: "Delayed", variant: "outline" },
    };
    const m = map[status];
    return <Badge variant={m.variant}>{m.label}</Badge>;
}
