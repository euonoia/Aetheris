import { motion } from "framer-motion";
import { ScanEye, FileImage, Radio, Receipt, Bus, Target, Compass, ListChecks } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

const capabilities = [
  { icon: ScanEye, title: "Automatic Violation Detection", desc: "YOLOv8 computer vision continuously scans camera feeds for traffic violations in real time." },
  { icon: FileImage, title: "Evidence Generation", desc: "Every detection auto-captures image, timestamp, GPS location, and camera ID as verifiable evidence." },
  { icon: Radio, title: "Traffic Monitoring", desc: "Live road density, congestion analytics, and incident tracking across the barangay road network." },
  { icon: Receipt, title: "Citation Management", desc: "Digital citation issuance, payment tracking, and appeals handling in a centralized system." },
  { icon: Bus, title: "Public Transport Coordination", desc: "Route, schedule, and fleet dispatch tools to keep local transport running efficiently." },
];

export function SystemOverview() {
  return (
<<<<<<< HEAD
    <section id="overview" className="border-b border-border bg-primary/2 py-20">
=======
    <section id="overview" className="border-b border-border bg-secondary/30 py-20">
>>>>>>> 888b05ef1a788984a824dbaf2566fddb1265f32a
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-2xl text-center"
        >
<<<<<<< HEAD
          <Badge variant="default">System Overview</Badge>
=======
          <Badge variant="outline">System Overview</Badge>
>>>>>>> 888b05ef1a788984a824dbaf2566fddb1265f32a
          <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">Built for smarter, safer streets</h2>
          <p className="mt-3 text-muted-foreground">
            The system was developed to modernize how Barangay 178 records, verifies, and acts on traffic violations —
            replacing manual, paper-based enforcement with automated, evidence-backed workflows.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mx-auto mt-10 max-w-3xl"
        >
          <Tabs defaultValue="purpose" className="flex flex-col items-center">
            <TabsList>
              <TabsTrigger value="purpose" className="gap-1.5"><Compass className="h-3.5 w-3.5" /> Purpose</TabsTrigger>
              <TabsTrigger value="mission" className="gap-1.5"><Target className="h-3.5 w-3.5" /> Mission</TabsTrigger>
              <TabsTrigger value="objectives" className="gap-1.5"><ListChecks className="h-3.5 w-3.5" /> Objectives</TabsTrigger>
            </TabsList>

            <TabsContent value="purpose" className="w-full">
              <Card><CardContent className="p-6 text-center text-sm leading-relaxed text-muted-foreground">
                To provide Barangay 178 with a reliable, technology-driven tool for identifying and documenting traffic
                violations, reducing dependence on manual enforcement and giving officers verifiable digital evidence
                for every citation issued.
              </CardContent></Card>
            </TabsContent>
            <TabsContent value="mission" className="w-full">
              <Card><CardContent className="p-6 text-center text-sm leading-relaxed text-muted-foreground">
                To ensure safe, orderly, and efficient traffic and transport management for the residents of
                Barangay 178 through accurate detection, transparent documentation, and data-driven enforcement.
              </CardContent></Card>
            </TabsContent>
            <TabsContent value="objectives" className="w-full">
              <Card><CardContent className="p-6 text-sm leading-relaxed text-muted-foreground">
                <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  <li>• Automate violation detection using computer vision</li>
                  <li>• Generate tamper-evident digital evidence</li>
                  <li>• Centralize citation and penalty records</li>
                  <li>• Provide real-time traffic flow visibility</li>
                  <li>• Support data-driven enforcement decisions</li>
                  <li>• Improve coordination of public transport routes</li>
                </ul>
              </CardContent></Card>
            </TabsContent>
          </Tabs>
        </motion.div>

        <div className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {capabilities.map((c, i) => (
            <motion.div
              key={c.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              whileHover={{ y: -3 }}
            >
              <Card className="h-full transition-shadow hover:shadow-elevated">
                <CardHeader>
<<<<<<< HEAD
                  <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-accent">
=======
                  <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
>>>>>>> 888b05ef1a788984a824dbaf2566fddb1265f32a
                    <c.icon className="h-5 w-5" />
                  </span>
                  <CardTitle className="pt-2 text-sm">{c.title}</CardTitle>
                  <CardDescription className="text-xs leading-relaxed">{c.desc}</CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
