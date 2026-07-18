import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowRight, PlayCircle, ShieldCheck, Camera, TrendingUp, MapPin, Sparkles, Radio } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i = 0) => ({ opacity: 1, y: 0, transition: { duration: 0.5, delay: i * 0.08, ease: "easeOut" } }),
};

export function Hero() {
  return (
    <section id="home" className="relative overflow-hidden border-b border-border bg-grid">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-primary/[0.04] via-transparent to-background" />
      <div className="container relative grid grid-cols-1 items-center gap-12 py-16 lg:grid-cols-2 lg:py-24">
        {/* Left */}
        <motion.div initial="hidden" animate="show" variants={fadeUp} custom={0}>
          <motion.div variants={fadeUp} custom={0.5}>
            <Badge variant="outline" className="gap-1.5 border-primary/30 text-primary">
              <ShieldCheck className="h-3.5 w-3.5" /> Official LGU Digital Platform
            </Badge>
          </motion.div>

          <motion.h1 variants={fadeUp} custom={1} className="mt-5 font-display text-4xl font-extrabold leading-[1.1] tracking-tight sm:text-5xl">
            Traffic and Transport <span className="text-primary">Management System</span>
          </motion.h1>

          <motion.p variants={fadeUp} custom={1.5} className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground">
            A professional, AI-powered platform for intelligent traffic monitoring, automatic violation evidence
            generation, and transportation management for <span className="font-medium text-foreground">Barangay 178, Camarin, North Caloocan</span>.
          </motion.p>

          <motion.div variants={fadeUp} custom={2} className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button size="lg">
              <Link to="/app">Launch System <ArrowRight className="h-4 w-4" /></Link>
            </Button>
            <Button size="lg" variant="outline">
              <a href="#features"><PlayCircle className="h-4 w-4" /> View Features</a>
            </Button>
          </motion.div>

          <motion.div variants={fadeUp} custom={2.5} className="mt-10 grid grid-cols-3 gap-6 border-t border-border pt-6">
            <div>
              <p className="font-display text-2xl font-bold text-primary">94.6%</p>
              <p className="text-xs text-muted-foreground">Detection Accuracy</p>
            </div>
            <div>
              <p className="font-display text-2xl font-bold text-primary">6</p>
              <p className="text-xs text-muted-foreground">CCTV Nodes Online</p>
            </div>
            <div>
              <p className="font-display text-2xl font-bold text-primary">24/7</p>
              <p className="text-xs text-muted-foreground">Automated Monitoring</p>
            </div>
          </motion.div>
        </motion.div>

        {/* Right — dashboard mockup */}
        <motion.div
          initial={{ opacity: 0, scale: 0.94, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
          className="relative"
        >
          <Card className="relative overflow-hidden shadow-elevated">
            <div className="flex items-center justify-between border-b border-border bg-secondary/50 px-4 py-3">
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-destructive/60" />
                <span className="h-2.5 w-2.5 rounded-full bg-[hsl(var(--warning))]/60" />
                <span className="h-2.5 w-2.5 rounded-full bg-primary/60" />
              </div>
              <span className="flex items-center gap-1 text-[11px] font-medium text-muted-foreground">
                <Radio className="h-3 w-3 text-destructive" /> Live Monitoring
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 p-4">
              <div className="col-span-3 grid grid-cols-3 gap-3">
                {[
                  { label: "Today's Violations", value: "17", tone: "text-destructive" },
                  { label: "Active Cameras", value: "6/6", tone: "text-primary" },
                  { label: "Officers On Duty", value: "8", tone: "text-foreground" },
                ].map((s) => (
                  <div key={s.label} className="rounded-md border border-border bg-card p-2.5">
                    <p className="text-[10px] text-muted-foreground">{s.label}</p>
                    <p className={`font-display text-lg font-bold ${s.tone}`}>{s.value}</p>
                  </div>
                ))}
              </div>

              {/* mini yolo preview */}
              <div className="col-span-2 relative aspect-[4/3] overflow-hidden rounded-md border border-border bg-[#0d130d]">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_25%,rgba(76,175,107,0.18),transparent_45%)]" />
                <div className="absolute left-[18%] top-[28%] h-[38%] w-[26%] rounded-sm border-2 border-accent">
                  <span className="absolute -top-4 left-0 whitespace-nowrap rounded bg-accent px-1 py-0.5 text-[8px] font-semibold text-white">Motorcycle 96%</span>
                </div>
                <div className="absolute left-[55%] top-[42%] h-[30%] w-[30%] rounded-sm border-2 border-primary">
                  <span className="absolute -top-4 left-0 whitespace-nowrap rounded bg-primary px-1 py-0.5 text-[8px] font-semibold text-white">Sedan 91%</span>
                </div>
                <span className="absolute left-2 top-2 flex items-center gap-1 rounded bg-black/50 px-1.5 py-0.5 text-[8px] font-mono text-white">
                  <Camera className="h-2.5 w-2.5" /> YOLOv8 · CAM-01
                </span>
              </div>

              {/* mini heatmap */}
              <div className="relative aspect-[4/3] overflow-hidden rounded-md border border-border bg-secondary/50">
                <MapPin className="absolute left-[30%] top-[35%] h-4 w-4 text-destructive" />
                <MapPin className="absolute left-[55%] top-[55%] h-4 w-4 text-accent" />
                <MapPin className="absolute left-[65%] top-[25%] h-3.5 w-3.5 text-primary" />
                <span className="absolute bottom-1 left-1 text-[8px] text-muted-foreground">Heatmap</span>
              </div>

              <div className="col-span-3 rounded-md border border-border p-3">
                <div className="flex items-center justify-between">
                  <p className="text-[11px] font-medium text-muted-foreground">Traffic Density — Camarin Rd.</p>
                  <span className="text-[11px] font-semibold text-destructive">78%</span>
                </div>
                  <Progress value={78} className="mt-1.5 h-1.5" />
              </div>
            </div>
          </Card>

          {/* floating AI insight card */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="absolute -right-6 -top-6 hidden w-52 rounded-lg border border-primary/20 bg-card p-3 shadow-elevated sm:block"
          >
            <p className="flex items-center gap-1.5 text-[11px] font-semibold text-primary"><Sparkles className="h-3.5 w-3.5" /> AI Risk Insight</p>
            <p className="mt-1 text-[11px] text-muted-foreground">Zabarte Rd. junction — high risk</p>
            <p className="mt-1 font-display text-xl font-bold text-destructive">82%</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.9 }}
            className="absolute -bottom-6 -left-6 hidden w-48 rounded-lg border border-border bg-card p-3 shadow-elevated sm:block"
          >
            <p className="flex items-center gap-1.5 text-[11px] font-semibold"><TrendingUp className="h-3.5 w-3.5 text-primary" /> Citations Today</p>
            <p className="mt-1 font-display text-xl font-bold">12</p>
            <p className="text-[10px] text-primary">+9.4% vs yesterday</p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
