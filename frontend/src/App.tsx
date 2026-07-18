import { Route, Routes } from "react-router-dom";
import { ThemeProvider } from "@/hooks/use-theme";
import DashboardPage from "@/pages/DashboardPage";
import LandingPage from "./pages/landing/LandingPage";
import OldDashboard from "./pages/OldDashboard";

function App() {
    return (
        <ThemeProvider>
        <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/old-dashboard" element={<OldDashboard />} />
            <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
        </ThemeProvider>
    );
}

export default App;