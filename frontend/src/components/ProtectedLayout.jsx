import React, { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { Menu, X } from "lucide-react";
import Sidebar from "./Sidebar.jsx";
import { useApp } from "../context/AppContext.jsx";

export default function ProtectedLayout({ children }) {
  const { token, loading, user } = useApp();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-400">
        Loading HUSTLE…
      </div>
    );
  }
  if (!token) return <Navigate to="/login" replace />;
  
  // Redirect to onboarding if not completed (but not if already on onboarding page)
  if (user && !user.onboardingCompleted && location.pathname !== "/onboarding") {
    return <Navigate to="/onboarding" replace />;
  }

  // Onboarding page has its own layout
  if (location.pathname === "/onboarding") {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen">
      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 bg-ink-900 border-b border-ink-700 px-4 py-3 flex items-center justify-between">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-ink-800"
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>
        <span className="font-display text-white">HUSTLE</span>
        <div className="w-9" />
      </div>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-50 bg-black/60"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar — drawer on mobile, fixed on desktop */}
      <div
        className={`fixed md:sticky top-0 z-50 h-screen transition-transform duration-300 md:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        } md:block`}
      >
        <Sidebar onNavigate={() => setMobileOpen(false)} />
        <button
          onClick={() => setMobileOpen(false)}
          className="md:hidden absolute top-4 right-[-3rem] p-2 text-white bg-ink-800 rounded-lg"
          aria-label="Close menu"
        >
          <X size={18} />
        </button>
      </div>

      <main className="flex-1 p-4 md:p-8 pt-16 md:pt-8 max-w-[1400px]">{children}</main>
    </div>
  );
}
