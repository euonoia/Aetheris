import { motion } from "framer-motion";
import { Landmark, Users, MapPinned, ShieldCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Separator } from "@/components/ui/separator";

const stats = [
  { icon: Users, label: "Residents Served", value: "~38,000" },
  { icon: MapPinned, label: "Roads Monitored", value: "12 km" },
  { icon: ShieldCheck, label: "CCTV Nodes", value: "6 Active" },
];

export function AboutBarangay() {
  return (
    <section id="about" className="border-b border-border bg-primary/2 py-20">
      <div className="container grid grid-cols-1 gap-12 lg:grid-cols-2 lg:items-start">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
        >
          <Badge variant="default" className="gap-1.5"><Landmark className="h-3.5 w-3.5" /> About Barangay 178</Badge>
          <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">Camarin, North Caloocan</h2>
          <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
            Barangay 178 is one of the residential communities within Camarin, North Caloocan City — a busy corridor
            connecting local residents to major thoroughfares. Traffic volume along its main roads has grown steadily,
            making organized, evidence-based enforcement a public safety priority for the barangay council.
          </p>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
            This platform was developed to support the barangay's traffic enforcers and officials with tools that
            were previously only available to larger city-level traffic authorities — brought down to the barangay
            level where most day-to-day enforcement actually happens.
          </p>

          <div className="mt-8 grid grid-cols-3 gap-4">
            {stats.map((s) => (
              <div key={s.label} className="rounded-lg border border-border bg-card p-4 text-center">
                <s.icon className="mx-auto h-5 w-5 text-primary" />
                <p className="mt-2 font-display text-lg font-bold">{s.value}</p>
                <p className="text-[11px] text-muted-foreground">{s.label}</p>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card>
            <CardContent className="p-6">
              <p className="mb-2 text-sm font-semibold">Learn more about the initiative</p>
              <Separator className="mb-3" />
              <Accordion>
                <AccordionItem value="coverage">
                  <AccordionTrigger>Coverage Area</AccordionTrigger>
                  <AccordionContent>
                    Six CCTV-equipped intersections along Camarin Road, Zabarte Road, and adjoining barangay streets,
                    covering the highest-traffic segments identified by the barangay traffic committee.
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="team">
                  <AccordionTrigger>Enforcement Team</AccordionTrigger>
                  <AccordionContent>
                    A rotating team of barangay traffic enforcers and auxiliary officers review AI-flagged detections
                    and coordinate directly with the barangay captain's office on citation issuance.
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="legal">
                  <AccordionTrigger>Legal Basis</AccordionTrigger>
                  <AccordionContent>
                    Enforcement follows existing barangay traffic ordinances and City of Caloocan traffic regulations;
                    the system digitizes and standardizes an already-authorized enforcement process.
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="data">
                  <AccordionTrigger>Data Handling</AccordionTrigger>
                  <AccordionContent>
                    Evidence images and vehicle records are retained according to barangay records-retention policy
                    and are accessible only to authorized enforcement and administrative accounts.
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  );
}
