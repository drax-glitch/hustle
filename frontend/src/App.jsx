import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedLayout from "./components/ProtectedLayout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Quests from "./pages/Quests.jsx";
import Character from "./pages/Character.jsx";
import Skills from "./pages/Skills.jsx";
import Achievements from "./pages/Achievements.jsx";
import Shop from "./pages/Shop.jsx";
import Progress from "./pages/Progress.jsx";
import Settings from "./pages/Settings.jsx";
import Onboarding from "./pages/Onboarding.jsx";
import World from "./pages/World.jsx";
import BossDetail from "./pages/BossDetail.jsx";
import BossCreate from "./pages/BossCreate.jsx";
import Chronicle from "./pages/Chronicle.jsx";
import Login from "./pages/Login.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/world" element={<ProtectedLayout><World /></ProtectedLayout>} />
      <Route path="/world/:regionId" element={<ProtectedLayout><World /></ProtectedLayout>} />
      <Route path="/boss/create" element={<ProtectedLayout><BossCreate /></ProtectedLayout>} />
      <Route path="/boss/:id" element={<ProtectedLayout><BossDetail /></ProtectedLayout>} />
      <Route path="/quests" element={<ProtectedLayout><Quests /></ProtectedLayout>} />
      <Route path="/character" element={<ProtectedLayout><Character /></ProtectedLayout>} />
      <Route path="/skills" element={<ProtectedLayout><Skills /></ProtectedLayout>} />
      <Route path="/chronicle" element={<ProtectedLayout><Chronicle /></ProtectedLayout>} />
      <Route path="/achievements" element={<ProtectedLayout><Achievements /></ProtectedLayout>} />
      <Route path="/shop" element={<ProtectedLayout><Shop /></ProtectedLayout>} />
      <Route path="/progress" element={<ProtectedLayout><Progress /></ProtectedLayout>} />
      <Route path="/settings" element={<ProtectedLayout><Settings /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
