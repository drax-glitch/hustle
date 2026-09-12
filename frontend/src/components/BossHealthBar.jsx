import React from "react";

export default function BossHealthBar({ currentHp, maxHp, currentPhase, phaseName, status }) {
  const hpPercent = Math.round((currentHp / maxHp) * 100);

  return (
    <div className="space-y-2">
      <div className="h-4 bg-ink-900 rounded-full overflow-hidden border border-ink-700">
        <div
          className={`h-full bg-gradient-to-r transition-all duration-500 ${
            status === "defeated"
              ? "from-emerald-500 to-emerald-400"
              : "from-rose-500 to-rose-400"
          }`}
          style={{ width: `${hpPercent}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-slate-500">
        <span>Phase {currentPhase} — {phaseName}</span>
        <span>{currentHp} / {maxHp} HP ({hpPercent}%)</span>
      </div>
    </div>
  );
}
