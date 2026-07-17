import { Route, Routes } from "react-router-dom";
import { ThemeProvider } from "@/hooks/use-theme";
import { ViolationRecordingPage } from "@/pages/ViolationRecordingPage";
import LandingPage from "./pages/landing/LandingPage";
import DashboardPage from "./pages/DashboardPage";

function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<DashboardPage />} />
        <Route path="/violation-recording" element={<ViolationRecordingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </ThemeProvider>
  );
}

export default App;