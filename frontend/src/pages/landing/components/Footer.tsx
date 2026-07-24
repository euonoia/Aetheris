import { Link } from "react-router-dom";
import { ShieldCheck, Mail, Phone } from "lucide-react";
import Facebook from '@/components/icons/Facebook';
import { Separator } from "@/components/ui/separator";
import {
  Menubar, MenubarMenu, MenubarTrigger, MenubarContent, MenubarItem, MenubarSeparator,
} from "@/components/ui/menubar";

const moduleLinks = [
  { title: "Violation Recording", href: "#modules" },
  { title: "Vehicle Monitoring", href: "#modules" },
  { title: "Traffic Flow Monitoring", href: "#modules" },
  { title: "Public Transport", href: "#modules" },
  { title: "Citations & Penalties", href: "#modules" },
];

const quickLinks = [
  { title: "Home", href: "#home" },
  { title: "Features", href: "#features" },
  { title: "About", href: "#about" },
  { title: "Contact", href: "#contact" },
];

export function Footer() {
  return (
    <footer className="bg-card">
      <div className="container py-4">
        <Menubar className="w-fit">
          <MenubarMenu>
            <MenubarTrigger>System</MenubarTrigger>
            <MenubarContent>
              <MenubarItem><a href="#modules">All Modules</a></MenubarItem>
              <MenubarItem><a href="#ai">AI Capabilities</a></MenubarItem>
              <MenubarItem><Link to="/app">Launch Dashboard</Link></MenubarItem>
            </MenubarContent>
          </MenubarMenu>
          <MenubarMenu>
            <MenubarTrigger>Support</MenubarTrigger>
            <MenubarContent>
              <MenubarItem><a href="#contact">Contact Office</a></MenubarItem>
              <MenubarItem><a href="#faq">Help Center</a></MenubarItem>
            </MenubarContent>
          </MenubarMenu>
          <MenubarMenu>
            <MenubarTrigger>Legal</MenubarTrigger>
            <MenubarContent>
              <MenubarItem><a href="#privacy">Privacy Policy</a></MenubarItem>
              <MenubarItem><a href="#terms">Terms of Use</a></MenubarItem>
              <MenubarSeparator />
              <MenubarItem><a href="#data">Data Handling Notice</a></MenubarItem>
            </MenubarContent>
          </MenubarMenu>
        </Menubar>
      </div>

      <Separator />

      <div className="container grid grid-cols-1 gap-8 py-12 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <ShieldCheck className="h-5 w-5" />
            </span>
            <span className="leading-tight">
              <span className="block font-display text-sm font-bold">Barangay 178 TMS</span>
              <span className="block text-[11px] text-muted-foreground">Camarin, North Caloocan</span>
            </span>
          </div>
          <p className="mt-4 text-xs leading-relaxed text-muted-foreground">
            An official traffic and transport management platform developed for Barangay 178, supporting local
            enforcement and public safety initiatives through AI-assisted monitoring.
          </p>
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Quick Links</p>
          <ul className="mt-3 space-y-2">
            {quickLinks.map((l) => (
              <li key={l.title}><a href={l.href} className="text-xs text-muted-foreground hover:text-foreground transition-colors">{l.title}</a></li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">System Modules</p>
          <ul className="mt-3 space-y-2">
            {moduleLinks.map((l) => (
              <li key={l.title}><a href={l.href} className="text-xs text-muted-foreground hover:text-foreground transition-colors">{l.title}</a></li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Barangay Office</p>
          <ul className="mt-3 space-y-2 text-xs text-muted-foreground">
            <li className="flex items-center gap-1.5"><Phone className="h-3.5 w-3.5" /> (02) 8123-4567</li>
            <li className="flex items-center gap-1.5"><Mail className="h-3.5 w-3.5" /> traffic@brgy178camarin.gov.ph</li>
            <li className="flex items-center gap-1.5"><Facebook className="h-3.5 w-3.5" /> /Barangay178Camarin</li>
          </ul>
        </div>
      </div>

      <Separator />

      <div className="container flex flex-col items-center justify-between gap-3 py-6 text-xs text-muted-foreground sm:flex-row">
        <p>© {new Date().getFullYear()} Barangay 178, Camarin, North Caloocan. All rights reserved.</p>
        <div className="flex items-center gap-4">
          <a href="#privacy" className="hover:text-foreground transition-colors">Privacy Policy</a>
          <a href="#terms" className="hover:text-foreground transition-colors">Terms</a>
        </div>
      </div>
    </footer>
  );
}
