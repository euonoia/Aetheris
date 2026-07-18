import { motion } from "framer-motion";
import { Gauge, FileX2, LineChart, ShieldCheck, Database, Zap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const benefits = [
  { icon: Gauge, title: "Improves Enforcement Efficiency", desc: "Officers spend less time on manual spotting and more on validation and response." },
  { icon: FileX2, title: "Reduces Manual Recording", desc: "Evidence is captured and structured automatically at the point of detection." },
  { icon: LineChart, title: "Supports Data-Driven Decisions", desc: "Trends and hotspots are visible instantly, guiding where resources go next." },
  { icon: ShieldCheck, title: "Enhances Public Safety", desc: "Consistent monitoring discourages repeat violations along high-risk corridors." },
  { icon: Database, title: "Centralized Traffic Information", desc: "Violations, vehicles, and citations live in one searchable, auditable system." },
  { icon: Zap, title: "Faster Evidence Processing", desc: "From detection to citation, records move through the workflow in minutes, not days." },
];

export function Benefits() {
  return (
    <section className="border-b border-border py-20">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-2xl text-center"
        >
          <Badge variant="default">Benefits</Badge>
          <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">Why Barangay 178 adopted this system</h2>
        </motion.div>

        <div className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {benefits.map((b, i) => (
            <motion.div
              key={b.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              whileHover={{ y: -3 }}
            >
              <Card className="h-full">
                <CardContent className="flex items-start gap-3 p-5">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <b.icon className="h-5 w-5" />
                  </span>
                  <div>
                    <p className="text-sm font-semibold leading-snug">{b.title}</p>
                    <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{b.desc}</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
