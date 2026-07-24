import { motion } from "framer-motion";
import { Camera, ScanEye, FileImage, UserCheck, Receipt, Database, BarChart3, ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

const steps = [
  { icon: Camera, title: "Camera Feed", desc: "CCTV nodes capture live footage across barangay roads." },
  { icon: ScanEye, title: "YOLOv8 Detection", desc: "AI model scans frames and flags traffic violations." },
  { icon: FileImage, title: "Evidence Generated", desc: "Image, timestamp, GPS, and confidence score are saved." },
  { icon: UserCheck, title: "Officer Validation", desc: "A traffic officer reviews and confirms the detection." },
  { icon: Receipt, title: "Citation Generated", desc: "A digital citation is issued to the registered owner." },
  { icon: Database, title: "Stored in Database", desc: "Records are centralized for audit and retrieval." },
  { icon: BarChart3, title: "Reports & Analytics", desc: "Trends and performance are surfaced for decision-making." },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="border-b border-border bg-primary/2 py-20">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-2xl text-center"
        >
          <Badge variant="default">How It Works</Badge>
          <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">From detection to decision, fully traceable</h2>
          <p className="mt-3 text-muted-foreground">Every violation follows the same auditable path — no step is skipped, nothing is manually re-typed.</p>
        </motion.div>

        <ScrollArea className="mt-12 w-full">
          <div className="flex gap-2 pb-6" style={{ width: "max-content" }}>
            {steps.map((s, i) => (
              <motion.div
                key={s.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.4, delay: i * 0.07 }}
                className="flex shrink-0 items-center"
              >
                <div className="flex w-44 flex-col items-center rounded-lg border border-border bg-card p-4 text-center shadow-soft sm:w-48">
                  <span className="flex h-11 w-11 items-center justify-center rounded-full bg-secondary text-accent">
                    <s.icon className="h-5 w-5" />
                  </span>
                  <span className="mt-2 text-[11px] font-semibold text-muted-foreground">Step {i + 1}</span>
                  <p className="mt-1 whitespace-normal text-sm font-semibold leading-snug">{s.title}</p>
                  <p className="mt-1.5 whitespace-normal text-xs leading-relaxed text-muted-foreground">{s.desc}</p>
                </div>
                {i < steps.length - 1 && <ArrowRight className="mx-2 h-4 w-4 shrink-0 text-border" />}
              </motion.div>
            ))}
          </div>
        </ScrollArea>
      </div>
    </section>
  );
}
