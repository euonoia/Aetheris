import { useState } from "react";
import { motion } from "framer-motion";
import { Camera, Car, Radio, Bus, Receipt, ArrowRight, Check } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Link } from "react-router-dom";

const modules = [
  {
    icon: Camera,
    title: "Traffic Violation Recording",
    desc: "YOLOv8-powered live detection with automatic evidence capture and officer review.",
    features: ["Live camera detection", "Bounding box preview", "Evidence gallery", "Officer verification workflow"],
  },
  {
    icon: Car,
    title: "Vehicle Monitoring",
    desc: "Search and verify vehicles by plate number with full violation and citation history.",
    features: ["QR code verification", "Owner information lookup", "Risk-level classification", "Blacklist flagging"],
  },
  {
    icon: Radio,
    title: "Traffic Flow Monitoring",
    desc: "Live density readings and congestion analytics across barangay intersections.",
    features: ["Real-time density dashboard", "Incident feed", "Predictive congestion alerts", "Interactive map overlay"],
  },
  {
    icon: Bus,
    title: "Public Transport Coordination",
    desc: "Route, schedule, and dispatch tools to keep local transport moving efficiently.",
    features: ["Route & schedule management", "Fleet status tracking", "Demand forecasting", "Dispatch recommendations"],
  },
  {
    icon: Receipt,
    title: "Citation & Penalty Management",
    desc: "End-to-end digital ticketing from issuance through payment and appeals.",
    features: ["Digital citation issuance", "Payment status tracking", "Appeals handling", "Revenue reporting"],
  },
];

export function SystemModules() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const active = openIndex !== null ? modules[openIndex] : null;

  return (
    <section id="modules" className="border-b border-border py-20">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-2xl text-center"
        >
          <Badge variant="default">System Modules</Badge>
          <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">Five modules, one enforcement platform</h2>
          <p className="mt-3 text-muted-foreground">Each module is purpose-built for a specific part of the enforcement workflow.</p>
        </motion.div>

        <div className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {modules.map((m, i) => (
            <motion.div
              key={m.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              whileHover={{ y: -4 }}
              className={i === 3 ? "sm:col-span-2 lg:col-span-1" : ""}
            >
              <Card className="flex h-full flex-col transition-shadow hover:shadow-elevated hover:border-primary/30">
                <CardHeader>
                  <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-secondary text-accent">
                    <m.icon className="h-5 w-5" />
                  </span>
                  <CardTitle className="pt-2 text-base">{m.title}</CardTitle>
                  <CardDescription className="text-xs leading-relaxed">{m.desc}</CardDescription>
                </CardHeader>
                <CardContent className="mt-auto pt-0">
                  <ul className="mb-4 space-y-1.5 text-xs text-muted-foreground">
                    {m.features.slice(0, 3).map((f) => (
                      <li key={f} className="flex items-center gap-1.5"><Check className="h-3 w-3 text-primary" /> {f}</li>
                    ))}
                  </ul>
                  <Button variant="outline" size="sm" className="w-full" onClick={() => setOpenIndex(i)}>
                    View More <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>

      <Dialog open={openIndex !== null} onOpenChange={(o) => !o && setOpenIndex(null)}>
        <DialogContent>
          {active && (
            <>
              <DialogHeader>
                <span className="mb-1 flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <active.icon className="h-5 w-5" />
                </span>
                <DialogTitle>{active.title}</DialogTitle>
                <DialogDescription>{active.desc}</DialogDescription>
              </DialogHeader>
              <ul className="space-y-2 text-sm">
                {active.features.map((f) => (
                  <li key={f} className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> {f}</li>
                ))}
              </ul>
              <DialogFooter>
                <Button variant="outline" onClick={() => setOpenIndex(null)}>Close</Button>
                <Button><Link to="/app">Open in Dashboard <ArrowRight className="h-3.5 w-3.5" /></Link></Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </section>
  );
}
