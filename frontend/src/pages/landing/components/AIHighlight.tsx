import { motion } from "framer-motion";
import { ScanEye, FileImage, Tags, Car, Gauge, Lightbulb, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";

const aiCards = [
  { icon: ScanEye, title: "YOLOv8 Detection", desc: "Object detection model trained to recognize vehicles and traffic violations from live video frames." },
  { icon: FileImage, title: "Automatic Evidence Generation", desc: "Every confirmed detection is packaged into a complete evidence record without manual data entry." },
  { icon: Tags, title: "Violation Recognition", desc: "Classifies violation type — illegal parking, beating the red light, no helmet, and more." },
  { icon: Car, title: "Vehicle Classification", desc: "Distinguishes motorcycles, sedans, jeepneys, vans, and utility vehicles for accurate records." },
  { icon: Gauge, title: "Confidence Scoring", desc: "Each detection carries a confidence percentage so officers can prioritize review." },
  { icon: Lightbulb, title: "Future AI Integration", desc: "Roadmap includes predictive congestion modeling and automated officer deployment suggestions." },
];

export function AIHighlight() {
  return (
    <section id="ai" className="border-b border-border bg-primary/2 py-20">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 items-center gap-10 lg:grid-cols-2"
        >
          <div>
            <Badge variant="default" className="gap-1.5"><Sparkles className="h-3.5 w-3.5" /> Artificial Intelligence at Work</Badge>
            <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">Computer vision that supports officers, not replaces them</h2>
            <p className="mt-3 text-muted-foreground">
              The YOLOv8 model flags likely violations and prepares evidence automatically — every detection still
              goes through officer validation before a citation is issued.
            </p>
          </div>

          <Card className="border-primary/20 bg-gradient-to-b from-primary/[0.04] to-transparent">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm">
                <span className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/15 text-primary"><ScanEye className="h-3.5 w-3.5" /></span>
                Sample Detection Output
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Vehicle Type</span><span className="font-medium">Motorcycle</span></div>
              <div className="flex items-center justify-between"><span className="text-muted-foreground">Violation</span><span className="font-medium">Illegal Parking</span></div>
              <div>
                <div className="flex items-center justify-between text-xs"><span className="text-muted-foreground">Confidence Score</span><span className="font-semibold">96%</span></div>
                <Progress value={96} className="mt-1.5 h-1.5" />
              </div>
              <div>
                <div className="flex items-center justify-between text-xs"><span className="text-muted-foreground">Plate Recognition Confidence</span><span className="font-semibold">88%</span></div>
                <Progress value={88} className="mt-1.5 h-1.5" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="mt-14"
        >
          <Carousel opts={{ align: "start", loop: true }}>
            <CarouselContent>
              {aiCards.map((c) => (
                <CarouselItem key={c.title} className="sm:basis-1/2 lg:basis-1/3">
                  <Card className="h-full">
                    <CardHeader>
                      <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-secondary text-accent">
                        <c.icon className="h-5 w-5" />
                      </span>
                      <CardTitle className="pt-2 text-base">{c.title}</CardTitle>
                      <CardDescription className="text-xs leading-relaxed">{c.desc}</CardDescription>
                    </CardHeader>
                  </Card>
                </CarouselItem>
              ))}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
          </Carousel>
        </motion.div>
      </div>
    </section>
  );
}
