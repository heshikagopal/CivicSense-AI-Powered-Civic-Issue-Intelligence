import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { CitizenReportPage } from './pages/CitizenReportPage';
import { CitizenDashboardPage } from './pages/CitizenDashboardPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { IssueDetailPage } from './pages/IssueDetailPage';
import { MapIntelligencePage } from './pages/MapIntelligencePage';
import { AuthPage } from './pages/AuthPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/report" element={<CitizenReportPage />} />
            <Route path="/citizen" element={<CitizenDashboardPage />} />
            <Route path="/admin" element={<AdminDashboardPage />} />
            <Route path="/issues/:id" element={<IssueDetailPage />} />
            <Route path="/map" element={<MapIntelligencePage />} />
            <Route path="/auth" element={<AuthPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
