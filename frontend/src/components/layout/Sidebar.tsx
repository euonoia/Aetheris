import { NavLink } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  LayoutDashboard, Camera, Car, Radio, Bus, Receipt, BarChart3, Users, Settings,
} from "lucide-react";

interface NavEntry {
    title: string;
    href: string;
    icon: typeof LayoutDashboard;
    description: string;
}

const navGroups: { label: string; items: NavEntry[] }[] = [
{
    label: "Overview",
    items: [{ title: "Dashboard", href: "/app/dashboard", icon: LayoutDashboard, description: "Executive summary" }],
},
{
    label: "Enforcement",
    items: [
        { title: "Violation Recording", href: "/app/violations", icon: Camera, description: "YOLOv8 detection & evidence" },
        { title: "Vehicle Monitoring", href: "/app/vehicles", icon: Car, description: "Registry & risk profile" },
        { title: "Citations & Penalties", href: "/app/citations", icon: Receipt, description: "Tickets & payments" },
    ],
},
{
    label: "Traffic & Transport",
    items: [
        { title: "Traffic Flow Monitoring", href: "/app/traffic-flow", icon: Radio, description: "Density & congestion" },
        { title: "Public Transport", href: "/app/public-transport", icon: Bus, description: "Routes & dispatch" },
    ],
},
// {
//     label: "Insights & Admin",
//     items: [
//         { title: "Reports & Analytics", href: "/app/reports", icon: BarChart3, description: "Trends & exports" },
//         { title: "User Management", href: "/app/users", icon: Users, description: "Roles & permissions" },
//         { title: "Settings", href: "/app/settings", icon: Settings, description: "System configuration" },
//     ],
// },
];

export const flatNav = navGroups.flatMap((group) => group.items);

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {

    return (
        <div className="flex h-full flex-col bg-card">
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-border">
            {/* <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <ShieldCheck className="h-5 w-5" />
            </div> */}
            <div className="flex flex-col items-center w-full min-w-0">
                <p className="font-display text-sm font-bold leading-tight truncate">Barangay 178 TMS</p>
                <p className="text-xs text-muted-foreground truncate">Camarin, North Caloocan</p>
            </div>
        </div>

        <ScrollArea className="flex-1 px-3 py-4">
            <nav className="flex flex-col gap-5">
                {navGroups.map((group) => (
                    <div key={group.label}>
                    <p className="px-2.5 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{group.label}</p>
                    <div className="flex flex-col gap-0.5">
                        {group.items.map((item) => (
                        <NavLink
                            key={item.href}
                            to={item.href}
                            end={item.href === "/app"}
                            onClick={onNavigate}
                            className={({ isActive }) =>
                            cn(
                                "group flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm font-medium transition-colors",
                                isActive
                                ? "bg-primary/10 text-primary"
                                : "text-foreground/80 hover:bg-secondary hover:text-foreground"
                            )
                            }
                        >
                            <item.icon className="h-4 w-4 shrink-0" />
                            <span className="truncate">{item.title}</span>
                        </NavLink>
                        ))}
                    </div>
                    </div>
                ))}
            </nav>
        </ScrollArea>

       
        </div>
    );
}
