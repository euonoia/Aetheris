import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ShieldCheck, Menu, Camera, Car, Radio, Bus, Receipt, BarChart3, ArrowRight, Cctv, ScanEye, FileCheck2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import {
  NavigationMenu, NavigationMenuContent, NavigationMenuItem, NavigationMenuLink,
  NavigationMenuList, NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import { cn } from "@/lib/utils";

const featureLinks = [
  { title: "AI Violation Detection", href: "#features", icon: ScanEye, description: "YOLOv8 computer vision spots violations in real time." },
  { title: "Automatic Evidence", href: "#features", icon: Cctv, description: "Timestamped, geotagged evidence generated automatically." },
  { title: "Citation Management", href: "#features", icon: FileCheck2, description: "Digital tickets, payments, and appeals in one place." },
];

const moduleLinks = [
  { title: "Violation Recording", href: "#modules", icon: Camera },
  { title: "Vehicle Monitoring", href: "#modules", icon: Car },
  { title: "Traffic Flow Monitoring", href: "#modules", icon: Radio },
  { title: "Public Transport", href: "#modules", icon: Bus },
  { title: "Citations & Penalties", href: "#modules", icon: Receipt },
  { title: "Reports & Analytics", href: "#modules", icon: BarChart3 },
];

function ListItem({ title, href, icon: Icon, description, onClick }: { title: string; href: string; icon: typeof Camera; description?: string; onClick?: () => void }) {
  return (
    <NavigationMenuLink>
      <a href={href} onClick={onClick} className="flex items-start gap-3 rounded-md p-3 transition-colors hover:bg-secondary">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-secondary text-accent">
          <Icon className="h-4 w-4" />
        </span>
        <span>
          <span className="block text-sm font-medium">{title}</span>
          {description && <span className="mt-0.5 block text-xs text-muted-foreground">{description}</span>}
        </span>
      </a>
    </NavigationMenuLink>
  );
}

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <motion.header
      initial={{ y: -16, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="sticky top-0 z-50 border-b border-border bg-card/90 backdrop-blur supports-[backdrop-filter]:bg-card/75"
    >
      <div className="container flex h-16 items-center justify-between">
        <a href="#home" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ShieldCheck className="h-5 w-5" />
          </span>
          <span className="leading-tight">
            <span className="block font-display text-sm font-bold">Barangay 178 TMS</span>
            <span className="block text-[11px] text-muted-foreground">Camarin, North Caloocan</span>
          </span>
        </a>

        <nav className="hidden items-center gap-1 lg:flex">
          <Button variant="ghost" size="sm"><a href="#home">Home</a></Button>

          <NavigationMenu>
            <NavigationMenuList>
              <NavigationMenuItem>
                <NavigationMenuTrigger className="h-8 bg-transparent px-3 text-sm">Features</NavigationMenuTrigger>
                <NavigationMenuContent>
                  <div className="w-[380px] p-2">
                    {featureLinks.map((f) => <ListItem key={f.title} {...f} />)}
                  </div>
                </NavigationMenuContent>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuTrigger className="h-8 bg-transparent px-3 text-sm">Modules</NavigationMenuTrigger>
                <NavigationMenuContent>
                  <div className="grid w-[420px] grid-cols-2 gap-1 p-2">
                    {moduleLinks.map((m) => <ListItem key={m.title} {...m} />)}
                  </div>
                </NavigationMenuContent>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>

          <Button variant="ghost" size="sm"><a href="#about">About</a></Button>
          <Button variant="ghost" size="sm"><a href="#contact">Contact</a></Button>
        </nav>

        <div className="hidden items-center gap-2 lg:flex">
            <ThemeToggle />
            <Separator orientation="vertical" className="mx-1 h-6" />
            <Button variant="outline" size="sm"><Link to="/app/dashboard">Login</Link></Button>
            <Button size="sm">
                <Link className="flex flex-row gap-2" to="/app/dashboard">
                    Get Started 
                    <ArrowRight className="h-3.5 w-3.5" />
                </Link>
            </Button>
        </div>

        <div className="flex items-center gap-1 lg:hidden">
          <ThemeToggle />
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <Button variant="ghost" size="icon" onClick={() => setMobileOpen(true)} aria-label="Open menu">
              <Menu className="h-5 w-5" />
            </Button>
            <SheetContent side="right" className="w-80">
              <SheetTitle className="flex items-center gap-2 font-display text-sm">
                <ShieldCheck className="h-5 w-5 text-primary" /> Barangay 178 TMS
              </SheetTitle>
              <nav className="mt-6 flex flex-col gap-1">
                {[
                  { label: "Home", href: "#home" },
                  { label: "Features", href: "#features" },
                  { label: "Modules", href: "#modules" },
                  { label: "About", href: "#about" },
                  { label: "Contact", href: "#contact" },
                ].map((l) => (
                  <a
                    key={l.href}
                    href={l.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn("rounded-md px-3 py-2.5 text-sm font-medium hover:bg-secondary transition-colors")}
                  >
                    {l.label}
                  </a>
                ))}
              </nav>
              <Separator className="my-5" />
              <div className="flex flex-col gap-2">
                <Button variant="outline"><Link to="/app" onClick={() => setMobileOpen(false)}>Login</Link></Button>
                <Button><Link to="/app" onClick={() => setMobileOpen(false)}>Get Started</Link></Button>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </motion.header>
  );
}
