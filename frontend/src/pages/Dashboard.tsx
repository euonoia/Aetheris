import { AlertTriangle, Camera, FileClock, ShieldCheck, TrendingUp, Bus, Zap, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatCard } from "@/components/shared/StatCard";
import { AIInsightCard } from "@/components/shared/AIInsightCard";
import { ViolationStatusBadge } from "@/components/shared/StatusBadges";
import { MapPlaceholder } from "@/components/shared/MapPlaceholder";
import { violations, monthlyViolationTrend, topViolationLocations } from "@/data/mock-violations";
import { formatDateTime } from "@/lib/utils";
import { Link } from "react-router-dom";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RTooltip,
} from "recharts";

const recentActivity = violations.slice(0, 6);

const quickActions = [
  { label: "Review Detections", href: "/app/violations", icon: Camera },
  { label: "Issue Citation", href: "/app/citations", icon: FileClock },
  { label: "Check Vehicle", href: "/app/vehicles", icon: ShieldCheck },
  { label: "Dispatch Transport", href: "/app/public-transport", icon: Bus },
];

export function DashboardPage() {
  return (
    <div className="space-y-6">

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Today's Violations" value="17" icon={Camera} trend={12} tone="danger" />
        <StatCard label="Pending Citations" value="34" icon={FileClock} trend={-4} tone="accent" />
        <StatCard label="Active Enforcers" value="8 / 10" icon={ShieldCheck} trend={0} tone="accent" trendLabel="on duty now" />
        <StatCard label="Public Transport Status" value="94% On Time" icon={Bus} tone="accent" trend={2} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between space-y-0 pb-0">
            <div>
              <CardTitle>Traffic Violation Trend</CardTitle>
              {/* <CardDescription>Detected violations vs. citations issued, last 6 months</CardDescription> */}
            </div>
            <Badge variant="outline" className="gap-1"><TrendingUp className="h-3 w-3" /> +9.4%</Badge>
          </CardHeader>
          <CardContent className="pt-4">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={monthlyViolationTrend} margin={{ left: -20, right: 10 }}>
                <defs>
                  <linearGradient id="violationsFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--chart-2))" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="hsl(var(--chart-2))" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="citationsFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <RTooltip
                  contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: "hsl(var(--foreground))", fontWeight: 600 }}
                />
                <Area type="monotone" dataKey="violations" stroke="hsl(var(--chart-2))" fill="url(#violationsFill)" strokeWidth={2} name="Violations" />
                <Area type="monotone" dataKey="citations" stroke="hsl(var(--chart-1))" fill="url(#citationsFill)" strokeWidth={2} name="Citations" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <AIInsightCard />
        {/* <Card>
            <CardHeader>
                <CardTitle>Top Violation Locations</CardTitle>
                <CardDescription>Ranked by incident count this month</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
                {topViolationLocations.map((loc, i) => (
                <div key={loc.location} className="flex items-center gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-secondary text-xs font-semibold">{i + 1}</span>
                    <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{loc.location}</p>
                    <div className="mt-1 h-1.5 w-full rounded-full bg-secondary">
                        <div className="h-1.5 rounded-full bg-primary" style={{ width: `${(loc.count / topViolationLocations[0].count) * 100}%` }} />
                    </div>
                    </div>
                    <span className="shrink-0 text-sm font-semibold text-muted-foreground">{loc.count}</span>
                </div>
                ))}
            </CardContent>
        </Card> */}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Violation Heatmap</CardTitle>
            {/* <CardDescription>Concentration of detected incidents across Barangay 178</CardDescription> */}
          </CardHeader>
          <CardContent>
            <MapPlaceholder className="h-72" />
          </CardContent>
        </Card>


      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <div>
              <CardTitle>Recent Activity</CardTitle>
              {/* <CardDescription>Latest automated detections and officer actions</CardDescription> */}
            </div>
            <Button variant="ghost" size="sm">
              <Link to="/app/violations">View all <ArrowRight className="h-3.5 w-3.5" /></Link>
            </Button>
          </CardHeader>
          <CardContent className="space-y-1">
            {recentActivity.map((v) => (
              <div key={v.id} className="flex items-center gap-3 rounded-md px-2 py-2.5 hover:bg-primary/20 transition-colors">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-secondary">
                  <AlertTriangle className="h-4 w-4 text-accent" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{v.violationType} — {v.plateNumber}</p>
                  <p className="truncate text-xs text-muted-foreground">{v.location} · {formatDateTime(v.timestamp)}</p>
                </div>
                <ViolationStatusBadge status={v.status} />
              </div>
            ))}
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
