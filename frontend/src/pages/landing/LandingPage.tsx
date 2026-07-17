import { Navbar } from "./components/Navbar";
import { Hero } from "./components/Hero";
import { SystemOverview } from "./components/SystemOverview";
import { KeyFeatures } from "./components/KeyFeatures";
// import { HowItWorks } from "./components/HowItWorks";
// import { SystemModules } from "./components/SystemModules";
// import { AIHighlight } from "./components/AIHighlight";
// import { DashboardPreview } from "./components/DashboardPreview";
// import { Benefits } from "./components/Benefits";
// import { AboutBarangay } from "./components/AboutBarangay";
// import { Contact } from "./components/Contact";
// import { Footer } from "./components/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <Hero />
        <SystemOverview />
        <KeyFeatures />
        {/* 
        <HowItWorks />
        <SystemModules />
        <AIHighlight />
        <DashboardPreview />
        <Benefits />
        <AboutBarangay />
        <Contact /> */}
      </main>
      {/* <Footer /> */}
    </div>
  );
}
