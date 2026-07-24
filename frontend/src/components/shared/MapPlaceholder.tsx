import { MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

interface Pin {
  x: number;
  y: number;
  label: string;
  variant?: "primary" | "accent" | "danger";
}

const defaultPins: Pin[] = [
  { x: 32, y: 40, label: "Camarin Rd. x Zabarte Rd.", variant: "danger" },
  { x: 58, y: 62, label: "Araneta Ave. Junction", variant: "accent" },
  { x: 70, y: 30, label: "Public Market Access Rd.", variant: "danger" },
  { x: 44, y: 78, label: "Zabarte x Llano St.", variant: "primary" },
  { x: 20, y: 65, label: "Covered Court Front", variant: "primary" },
];

export function MapPlaceholder({ pins = defaultPins, className }: { pins?: Pin[]; className?: string }) {
  return (
    <div className={cn("relative w-full overflow-hidden rounded-lg border border-border bg-secondary/40 bg-grid", className)}>
        <div className="absolute inset-0 bg-gradient-to-br from-background/0 via-background/0 to-background/60" />
        {pins.map((pin, i) => (
            <div key={i} className="absolute -translate-x-1/2 -translate-y-full group" style={{ left: `${pin.x}%`, top: `${pin.y}%` }}>
            <div className="relative flex flex-col items-center">
                <span
                className={cn(
                    "flex h-7 w-7 items-center justify-center rounded-full shadow-elevated text-white",
                    pin.variant === "danger" && "bg-destructive",
                    pin.variant === "accent" && "bg-accent",
                    (pin.variant === "primary" || !pin.variant) && "bg-primary"
                )}
                >
                <MapPin className="h-3.5 w-3.5" />
                </span>
                <span className="mt-1 hidden whitespace-nowrap rounded-md bg-foreground px-2 py-0.5 text-[10px] font-medium text-background group-hover:block">
                {pin.label}
                </span>
            </div>
            </div>
        ))}
        <div className="absolute bottom-3 left-3 rounded-md bg-card/90 px-2.5 py-1.5 text-[11px] text-muted-foreground shadow-soft backdrop-blur">
            Map integration placeholder — Google Maps / Leaflet
        </div>
    </div>
  );
}
