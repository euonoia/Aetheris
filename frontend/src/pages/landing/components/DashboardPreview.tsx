import { motion } from "framer-motion";
import {
  LayoutDashboard, Camera, Car, Radio, Bus, Receipt, BarChart3, Users, Settings, Bell, MapPin,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { ResponsiveContainer, AreaChart, Area, XAxis } from "recharts";

const sidebarIcons = [LayoutDashboard, Camera, Car, Radio, Bus, Receipt, BarChart3, Users, Settings];

const trend = [
  { m: "Feb", v: 210 }, { m: "Mar", v: 244 }, { m: "Apr", v: 198 }, { m: "May", v: 267 }, { m: "Jun", v: 231 }, { m: "Jul", v: 189 },
];

const previewViolations = [
  { plate: "NDX 2291", type: "Illegal Parking", location: "Camarin Rd. x Zabarte Rd.", status: "Citation Issued" },
  { plate: "TYU 7734", type: "No Helmet", location: "Araneta Ave. Junction", status: "Under Review" },
  { plate: "WQR 4482", type: "Beating the Red Light", location: "Public Market Access Rd.", status: "Detected" },
];

const statusVariant: Record<string, "secondary" | "outline" | "destructive"> = {
  "Citation Issued": "secondary",
  "Under Review": "outline",
  "Detected": "destructive",
};

export function DashboardPreview() {
  return (
    <section id="dashboard-preview" className="border-b border-border py-20">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-2xl text-center"
        >
          <Badge variant="default">Inside the Platform</Badge>
          <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">A complete enforcement dashboard</h2>
          <p className="mt-3 text-muted-foreground">A preview of what officers and administrators see after logging in.</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.98 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="mt-12"
        >
          <Card className="overflow-hidden shadow-elevated">
            <div className="flex">
              <div className="hidden w-14 shrink-0 flex-col items-center gap-3 border-r border-border bg-card py-4 sm:flex">
                <span className="mb-2 flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground text-xs font-bold">B</span>
                {sidebarIcons.map((Icon, i) => (
                  <span key={i} className={`flex h-8 w-8 items-center justify-center rounded-md ${i === 0 ? "bg-primary/10 text-primary" : "text-muted-foreground"}`}>
                    <Icon className="h-4 w-4" />
                  </span>
                ))}
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between border-b border-border px-4 py-3">
                  <Breadcrumb>
                    <BreadcrumbList>
                      <BreadcrumbItem><BreadcrumbLink href="#">Barangay 178 TMS</BreadcrumbLink></BreadcrumbItem>
                      <BreadcrumbSeparator />
                      <BreadcrumbItem><BreadcrumbPage>Dashboard</BreadcrumbPage></BreadcrumbItem>
                    </BreadcrumbList>
                  </Breadcrumb>
                  <div className="flex items-center gap-2">
                    <Bell className="h-4 w-4 text-muted-foreground" />
                    <Avatar className="h-7 w-7"><AvatarFallback>CR</AvatarFallback></Avatar>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 p-4 lg:grid-cols-3">
                  <div className="grid grid-cols-3 gap-3 lg:col-span-3">
                    {[
                      { label: "Today's Violations", value: "17" },
                      { label: "Pending Citations", value: "34" },
                      { label: "Active Enforcers", value: "8/10" },
                    ].map((s) => (
                      <div key={s.label} className="rounded-md border border-border p-3">
                        <p className="text-[10px] text-muted-foreground">{s.label}</p>
                        <p className="font-display text-lg font-bold">{s.value}</p>
                      </div>
                    ))}
                  </div>

                  <div className="rounded-md border border-border p-3 lg:col-span-2">
                    <p className="mb-1 text-xs font-medium text-muted-foreground">Traffic Violation Trend</p>
                    <ResponsiveContainer width="100%" height={110}>
                      <AreaChart data={trend}>
                        <defs>
                          <linearGradient id="previewFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.35} />
                            <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="m" hide />
                        <Area type="monotone" dataKey="v" stroke="hsl(var(--chart-1))" fill="url(#previewFill)" strokeWidth={2} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="rounded-md border border-border p-3">
                    <p className="mb-2 text-xs font-medium text-muted-foreground">Officer Activity</p>
                    <div className="space-y-2">
                      {["PO2 Marasigan", "PO1 Delos Santos", "SPO1 Villareal"].map((o, i) => (
                        <div key={o} className="flex items-center justify-between text-[11px]">
                          <span className="truncate">{o}</span>
                          <Badge variant="outline" className="text-[9px]">{8 - i * 2} today</Badge>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-md border border-border p-3 lg:col-span-2">
                    <p className="mb-2 text-xs font-medium text-muted-foreground">Recent Detections</p>
                    <Table>
                      <TableHeader>
                        <TableRow><TableHead className="h-7 text-[10px]">Plate</TableHead><TableHead className="h-7 text-[10px]">Violation</TableHead><TableHead className="h-7 text-[10px]">Status</TableHead></TableRow>
                      </TableHeader>
                      <TableBody>
                        {previewViolations.map((v) => (
                          <TableRow key={v.plate}>
                            <TableCell className="py-1.5 font-mono text-[11px]">{v.plate}</TableCell>
                            <TableCell className="py-1.5 text-[11px]">{v.type}</TableCell>
                            <TableCell className="py-1.5"><Badge variant={statusVariant[v.status]} className="text-[9px]">{v.status}</Badge></TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>

                  <div className="rounded-md border border-border p-3">
                    <p className="mb-2 text-xs font-medium text-muted-foreground">Density Heatmap</p>
                    <div className="relative h-24 overflow-hidden rounded-md bg-secondary/60">
                      <MapPin className="absolute left-[30%] top-[30%] h-3.5 w-3.5 text-destructive" />
                      <MapPin className="absolute left-[60%] top-[55%] h-3.5 w-3.5 text-accent" />
                      <MapPin className="absolute left-[45%] top-[65%] h-3 w-3 text-primary" />
                    </div>
                    <div className="mt-2">
                      <div className="flex items-center justify-between text-[10px]"><span className="text-muted-foreground">Citation Rate</span><span className="font-semibold">76%</span></div>
                      <Progress value={76} className="mt-1 h-1" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  );
}
