import React from "react";

const ATTR_META = {
  strength: { label: "Strength", icon: "💪", color: "from-rose-500 to-rose-400" },
  intelligence: { label: "Intelligence", icon: "🧠", color: "from-sky-500 to-sky-400" },
  discipline: { label: "Discipline", icon: "🔥", color: "from-amber-500 to-amber-400" },
  creativity: { label: "Creativity", icon: "🎨", color: "from-purple-500 to-purple-400" },
  vitality: { label: "Vitality", icon: "❤️", color: "from-emerald-500 to-emerald-400" },
};

const TIER_COLORS = {
  Novice: "text-slate-400",
  Apprentice: "text-emerald-400",
  Skilled: "text-sky-400",
  Expert: "text-purple-400",
  Master: "text-amber-400",
  Legendary: "text-rose-400",
};

export default function AttributeBar({ name, value, max = 100, compact = false, tier }) {
  const meta = ATTR_META[name] || { label: name, icon: "✨", color: "from-slate-500 to-slate-400" };
  const pct = Math.min(100, (value / max) * 100);
  const tierColor = TIER_COLORS[tier] || "text-slate-400";

  return (
    <div className={compact ? "mb-3" : "mb-4.5"}>
      <div className="flex items-center justify-between mb-1.5 text-xs">
        <span className="flex items-center gap-1.5 text-slate-300 font-medium">
          <span className="text-sm">{meta.icon}</span> {meta.label}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-slate-200 font-mono font-bold text-xs">
            {value}
            {!compact && <span className="text-slate-500 font-normal"> / {max}</span>}
          </span>
          {tier && (
            <span className={`text-[10px] font-mono font-semibold uppercase tracking-wider px-1.5 py-0.2 rounded bg-ink-850 border border-ink-750 ${tierColor}`}>
              {tier}
            </span>
          )}
        </div>
      </div>
      <div className="progress-track h-1.5 bg-ink-850">
        <div
          className={`progress-fill bg-gradient-to-r ${meta.color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

