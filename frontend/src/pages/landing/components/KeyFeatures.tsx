import { motion } from "framer-motion";
import { ScanEye, FileImage, Radio, Car, Receipt, BrainCircuit } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";

const features = [
  {
    number: "01",
    icon: ScanEye,
    title: "Automatic Traffic Violation Detection",
    tag: "YOLOv8 Computer Vision",
    points: ["Real-time frame analysis", "Multi-class vehicle detection", "Configurable violation rules"],
  },
  {
    number: "02",
    icon: FileImage,
    title: "Automatic Evidence Generation",
    tag: "Tamper-evident records",
    points: ["Captured image", "Timestamp & Camera ID", "Location, violation type & confidence score"],
  },
  {
    number: "03",
    icon: Radio,
    title: "Traffic Flow Monitoring",
    tag: "Live road intelligence",
    points: ["Live traffic status", "Congestion analytics", "Density heatmaps"],
  },
  {
    number: "04",
    icon: Car,
    title: "Vehicle Monitoring",
    tag: "Registry & verification",
    points: ["Vehicle registry", "Violation & citation history", "Status verification"],
  },
  {
    number: "05",
    icon: Receipt,
    title: "Citation & Penalty Management",
    tag: "End-to-end ticketing",
    points: ["Digital citation issuance", "Payment status tracking", "Appeals & reports"],
  },
  {
    number: "06",
    icon: BrainCircuit,
    title: "Decision Support",
    tag: "AI-assisted enforcement",
    points: ["Traffic insights", "Deployment recommendations", "Trend analytics"],
  },
];

export function KeyFeatures() {
  return (
    <section id="features" className="border-b border-border py-20">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-2xl text-center"
        >
          <Badge variant="outline">Key Features</Badge>
          <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">Everything enforcement needs, in one platform</h2>
          <p className="mt-3 text-muted-foreground">Six core capabilities that work together across detection, evidence, and enforcement.</p>
        </motion.div>

        <div className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <motion.div
              key={f.number}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              whileHover={{ y: -4 }}
            >
              <HoverCard>
                <HoverCardTrigger delay={150}>
                    <Card className="h-full cursor-default transition-shadow hover:shadow-elevated hover:border-primary/30">
                        <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                            <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
                            <f.icon className="h-5 w-5" />
                            </span>
                            <span className="font-display text-2xl font-bold text-border">{f.number}</span>
                        </div>
                        <CardTitle className="pt-2 text-base leading-snug">{f.title}</CardTitle>
                        <Badge variant="secondary" className="w-fit text-[10px]">{f.tag}</Badge>
                        </CardHeader>
                        <CardContent className="pt-3">
                            <Separator className="mb-3" />
                            <ul className="space-y-1.5 text-xs text-muted-foreground">
                                {f.points.map((p) => <li key={p} className="flex items-start gap-1.5"><span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary" />{p}</li>)}
                            </ul>
                        </CardContent>
                    </Card>
                </HoverCardTrigger>
                <HoverCardContent side="top" className="text-xs text-muted-foreground">
                  Part of the {f.title} module — available after logging in to the enforcement dashboard.
                </HoverCardContent>
              </HoverCard>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
