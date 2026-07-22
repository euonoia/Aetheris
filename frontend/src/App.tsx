import { Route, Routes } from "react-router-dom";
import { ThemeProvider } from "@/hooks/use-theme";
import ViolationRecording from "@/pages/ViolationRecording";
import LandingPage from "./pages/landing/LandingPage";
import OldDashboard from "./pages/OldDashboard";
import { AppShell } from "#components/layout/AppShell";
import { DashboardPage } from "./pages/Dashboard";

function App() {
  return (
    <ThemeProvider>
        <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route element={<AppShell />}>
                <Route path="/app/dashboard" element={<DashboardPage />} />
                <Route path="/app/old-dashboard" element={<OldDashboard />} />
                <Route path="/app/violations" element={<ViolationRecording />} />
            </Route>
         </Routes>
    </ThemeProvider>
  );
}

export default App;