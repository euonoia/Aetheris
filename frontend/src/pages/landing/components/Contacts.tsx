import { useState } from "react";
import { motion } from "framer-motion";
import { MapPin, Phone, Mail, Clock, Send } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  AlertDialog, AlertDialogAction, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { cn } from "#lib/utils";


const contactDetails = [
  { icon: MapPin, label: "Office Address", value: "Barangay Hall, Camarin Road, Camarin, Caloocan City" },
  { icon: Phone, label: "Phone", value: "(02) 8123-4567" },
  { icon: Mail, label: "Email", value: "traffic@brgy178camarin.gov.ph" },
  { icon: Clock, label: "Office Hours", value: "Mon–Fri, 8:00 AM – 5:00 PM" },
];

export function Contact() {
  const [confirmOpen, setConfirmOpen] = useState(false);

    interface Pin {
        x: number;
        y: number;
        label: string;
        variant?: "primary" | "accent" | "danger";
    }

        const defaultPins: Pin[] = [
        { x: 32, y: 40, label: "Camarin Rd. x Zabarte Rd.", variant: "danger" },
        { x: 58, y: 62, label: "Araneta Ave. Junction", variant: "accent" },
        { x: 70, y: 30, label: "Public Market Access Rd.", variant: "danger" },
        { x: 44, y: 78, label: "Zabarte x Llano St.", variant: "primary" },
        { x: 20, y: 65, label: "Covered Court Front", variant: "primary" },
    ];

  return (
    <section id="contact" className="border-b border-border py-20">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-2xl text-center"
        >
          <Badge variant="default">Contact</Badge>
          <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">Get in touch with the barangay office</h2>
          <p className="mt-3 text-muted-foreground">Questions about a citation, vehicle record, or the platform itself? Reach out directly.</p>
        </motion.div>

        <div className="mt-12 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {contactDetails.map((c) => (
                <Card key={c.label}>
                  <CardContent className="flex items-start gap-3 p-4">
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-secondary text-accent">
                      <c.icon className="h-4 w-4" />
                    </span>
                    <div>
                      <p className="text-xs text-muted-foreground">{c.label}</p>
                      <p className="text-sm font-medium leading-snug">{c.value}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="relative h-56 w-full overflow-hidden rounded-lg border border-border bg-secondary/40 bg-grid">
                <div className="absolute inset-0 bg-gradient-to-br from-background/0 via-background/0 to-background/60" />
                {defaultPins.map((pin, i) => (
                    <div key={i} className="absolute -translate-x-1/2 -translate-y-full group" style={{ left: `${pin.x}%`, top: `${pin.y}%` }}>
                        <div className="relative flex flex-col items-center">
                            <span
                                className={cn(
                                    "flex h-7 w-7 items-center justify-center rounded-full shadow-elevated text-white",
                                    pin.variant === "danger" && "bg-destructive",
                                    pin.variant === "accent" && "bg-accent",
                                    (pin.variant === "primary" || !pin.variant) && "bg-primary"
                                )}
                                >
                                <MapPin className="h-3.5 w-3.5" />
                            </span>
                            <span className="mt-1 hidden whitespace-nowrap rounded-md bg-foreground px-2 py-0.5 text-[10px] font-medium text-background group-hover:block">
                                {pin.label}
                            </span>
                        </div>
                    </div>
                ))}
                <div className="absolute bottom-3 left-3 rounded-md bg-card/90 px-2.5 py-1.5 text-[11px] text-muted-foreground shadow-soft backdrop-blur">
                    Map integration placeholder — Google Maps / Leaflet
                </div>
            </div>      
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <CardContent className="p-6">
                <form
                  className="space-y-4"
                  onSubmit={(e) => {
                    e.preventDefault();
                    setConfirmOpen(true);
                  }}
                >
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="space-y-1.5">
                      <Label htmlFor="c-name">Full Name</Label>
                      <Input id="c-name" placeholder="Juan Dela Cruz" required />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="c-email">Email Address</Label>
                      <Input id="c-email" type="email" placeholder="you@email.com" required />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="c-subject">Subject</Label>
                    <Input id="c-subject" placeholder="e.g. Citation inquiry" required />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="c-message">Message</Label>
                    <Textarea id="c-message" placeholder="Tell us how we can help..." rows={5} required />
                  </div>
                  <Button type="submit" className="w-full"><Send className="h-4 w-4" /> Send Message</Button>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>

      <AlertDialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Message received</AlertDialogTitle>
            <AlertDialogDescription>
              Thank you for reaching out to Barangay 178. This is a frontend demo, so no message was actually sent —
              in production this would route to the barangay office's inbox.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogAction onClick={() => setConfirmOpen(false)}>Got it</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  );
}
