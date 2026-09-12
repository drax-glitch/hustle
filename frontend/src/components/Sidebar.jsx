import React from "react";
import { NavLink } from "react-router-dom";
import {
  Compass, CheckCircle2, User, Trophy, Store,
  BarChart3, Settings, Sparkles, Map, BookOpen,
} from "lucide-react";
import { useApp } from "../context/AppContext.jsx";

const NAV_GROUPS = [
  {
    group: "ADVENTURE",
    items: [
      { to: "/", label: "Dashboard", icon: Compass },
      { to: "/quests", label: "Quest Log", icon: CheckCircle2 },
      { to: "/world", label: "World Map", icon: Map },
    ],
  },
  {
    group: "PROGRESSION",
    items: [
      { to: "/character", label: "Character", icon: User },
      { to: "/skills", label: "Skills & Mastery", icon: Sparkles },
      { to: "/chronicle", label: "Daily Chronicle", icon: BookOpen },
    ],
  },
  {
    group: "ARSENAL & FEATS",
    items: [
      { to: "/shop", label: "The Emporium", icon: Store },
      { to: "/achievements", label: "Achievements", icon: Trophy },
      { to: "/progress", label: "Analytics", icon: BarChart3 },
      { to: "/settings", label: "Settings", icon: Settings },
    ],
  },
];

function HustleMark({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="6" width="5" height="20" rx="1.5" fill="#f59e0b" />
      <rect x="23" y="4" width="5" height="22" rx="1.5" fill="#f59e0b" />
      <path d="M9 18 L23 12" stroke="#f59e0b" strokeWidth="4.5" strokeLinecap="round" />
    </svg>
  );
}

export default function Sidebar({ onNavigate }) {
  const { user } = useApp();

  return (
    <aside className="w-64 shrink-0 bg-ink-900 border-r border-ink-800/80 flex flex-col h-screen select-none">
      {/* Brand */}
      <div className="px-6 py-5 border-b border-ink-800/60">
        <div className="flex items-center gap-3">
          <HustleMark size={22} />
          <div>
            <span className="font-display font-bold text-base tracking-tight text-white">HUSTLE</span>
            <p className="text-[10px] text-slate-500 tracking-wider uppercase font-medium">Your Life. Your Game.</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto">
        {NAV_GROUPS.map((group) => (
          <div key={group.group}>
            <p className="px-3 mb-1.5 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
              {group.group}
            </p>
            <div className="space-y-0.5">
              {group.items.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === "/"}
                  onClick={onNavigate}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 relative ${
                      isActive
                        ? "bg-amber-500/10 text-amber-300 font-semibold border-l-2 border-amber-500"
                        : "text-slate-400 hover:text-slate-200 hover:bg-ink-800/60"
                    }`
                  }
                >
                  <Icon size={16} className="shrink-0" />
                  <span className="truncate">{label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* User footer */}
      {user && (
        <div className="p-3 border-t border-ink-800/60 bg-ink-950/40">
          <div className="flex items-center gap-3 p-2.5 rounded-lg bg-ink-900/80 border border-ink-800/60">
            <div className="w-9 h-9 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-lg shrink-0">
              {user.avatar || "🧙"}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-1">
                <p className="text-xs font-bold text-slate-200 truncate">{user.displayName || "Hero"}</p>
                <span className="text-[10px] font-bold text-amber-400 font-mono">LVL {user.level}</span>
              </div>
              <div className="progress-track h-1 mt-1.5 bg-ink-800">
                <div
                  className="progress-fill bg-amber-500"
                  style={{ width: `${Math.min(100, (user.xp / (user.xpToNext || 100)) * 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
