import React from "react";

export default function StatPill({ icon, value, label, color = "text-arcane-400" }) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-ink-900 border border-ink-700/80 hover:border-ink-600 transition-colors">
      <span className={`${color} shrink-0`}>{icon}</span>
      <div className="leading-tight">
        <p className="text-xs font-bold text-slate-100 font-mono tracking-tight">{value}</p>
        {label && <p className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold">{label}</p>}
      </div>
    </div>
  );
}

