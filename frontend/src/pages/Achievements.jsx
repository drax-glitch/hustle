import React, { useEffect, useState } from "react";
import { Trophy, Check } from "lucide-react";
import * as api from "../api/api";
import LoadingState from "../components/LoadingState.jsx";

export default function Achievements() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.fetchAchievements().then(setData);
  }, []);

  if (!data) return <LoadingState label="Reviewing the hall of records…" />;

  const pct = Math.round((data.unlockedCount / data.totalCount) * 100);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <span className="eyebrow-amber">HALL OF FEATS</span>
          <h1 className="font-display text-3xl font-bold text-white tracking-tight mt-1">Heroic Achievements</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {data.unlockedCount} of {data.totalCount} feats unlocked
          </p>
        </div>
        <div className="px-3.5 py-1.5 rounded-lg bg-ink-900 border border-ink-700/80 text-arcane-400 font-mono font-bold text-sm">
          {pct}% Mastered
        </div>
      </div>

      <div className="space-y-2">
        <div className="progress-track h-2 bg-ink-800">
          <div className="progress-fill bg-gradient-to-r from-arcane-500 to-amber-300" style={{ width: `${pct}%` }} />
        </div>
        <div className="flex justify-between text-[11px] font-mono text-slate-400">
          <span>Progression</span>
          <span>{data.unlockedCount} / {data.totalCount}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {data.achievements.map((a) => (
          <div
            key={a.id}
            className={`panel p-4 sm:p-5 flex items-start gap-3.5 bg-ink-900 border transition-colors ${
              a.unlocked ? "border-ink-750" : "border-ink-800/60 opacity-50"
            }`}
          >
            <div
              className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl shrink-0 ${
                a.unlocked ? "bg-ink-850 border border-arcane-500/40" : "bg-ink-850 border border-ink-750"
              }`}
            >
              {a.unlocked ? a.icon : "🔒"}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-1">
                <p className="text-xs font-semibold text-slate-100 truncate">{a.title}</p>
                {a.unlocked && (
                  <span className="text-[9px] font-mono font-bold text-emerald-400 flex items-center gap-0.5">
                    <Check size={10} /> DONE
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-2 leading-tight">{a.description}</p>
              <p className={`text-[10px] font-mono mt-2 font-semibold ${a.unlocked ? "text-arcane-400" : "text-slate-500"}`}>
                +{a.xpReward} XP Reward
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

