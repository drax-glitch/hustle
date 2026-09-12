import React from "react";
import { Crown, Sparkles } from "lucide-react";

export default function CharacterEvolution({ evolution }) {
  if (!evolution) return null;

  const {
    stage,
    display,
    title,
    level,
    nextStage,
    nextDisplay,
    nextRequirement,
    progressPercent,
    levelsUntilNext,
  } = evolution;

  const progressPercentage =
    typeof progressPercent === "number"
      ? progressPercent
      : nextRequirement
      ? Math.max(0, Math.min(100, ((level - (nextRequirement - 10)) / 10) * 100))
      : 100;

  return (
    <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
      <div className="flex items-center justify-between mb-4">
        <span className="eyebrow-amber flex items-center gap-1.5">
          <Sparkles size={13} className="text-arcane-400" /> Progression Tier
        </span>
        <span className="text-[11px] font-mono text-slate-400">
          Rank {display}
        </span>
      </div>

      <div className="mb-4">
        <h3 className="font-display text-xl font-bold text-white tracking-tight">{title}</h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Current Standing · Level {level}
        </p>
      </div>

      {nextStage && nextRequirement ? (
        <div className="pt-3 border-t border-ink-800/80">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-slate-400 flex items-center gap-1">
              <Crown size={12} className="text-arcane-400" /> Next: <span className="text-slate-200 font-semibold">{nextDisplay}</span>
            </span>
            <span className="text-slate-400 font-mono text-[11px]">
              {levelsUntilNext !== undefined && levelsUntilNext > 0
                ? `${levelsUntilNext} levels to go (LVL ${nextRequirement})`
                : `LVL ${nextRequirement}`}
            </span>
          </div>
          <div className="progress-track h-2 bg-ink-800 mb-1">
            <div
              className="progress-fill bg-gradient-to-r from-arcane-500 to-amber-300"
              style={{ width: `${Math.min(100, Math.max(0, progressPercentage))}%` }}
            />
          </div>
          <div className="flex justify-end text-[10px] font-mono text-slate-500">
            {Math.round(progressPercentage)}% completed
          </div>
        </div>
      ) : (
        <div className="pt-3 border-t border-ink-800/80 text-xs text-arcane-400 font-semibold flex items-center gap-1.5">
          <Crown size={14} /> Pinnacle Rank Reached
        </div>
      )}
    </div>
  );
}

