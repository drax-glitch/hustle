import React from "react";
import { Lock, CheckCircle, Swords } from "lucide-react";

export default function BossPhase({ phase, index, currentPhase, totalPhases }) {
  const isCurrent = index === currentPhase - 1;
  const isCompleted = index < currentPhase - 1;
  const isLocked = index > currentPhase - 1;

  return (
    <div
      className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
        isCurrent
          ? "bg-rose-500/10 border-rose-500/50"
          : isCompleted
          ? "bg-emerald-500/10 border-emerald-500/30"
          : "bg-ink-800 border-ink-700 opacity-50"
      }`}
    >
      {isLocked ? (
        <Lock size={14} className="text-slate-600" />
      ) : isCompleted ? (
        <CheckCircle size={14} className="text-emerald-400" />
      ) : (
        <Swords size={14} className="text-rose-400" />
      )}
      <span
        className={`text-xs font-medium ${
          isCurrent
            ? "text-rose-400"
            : isCompleted
            ? "text-emerald-400"
            : "text-slate-500"
        }`}
      >
        {phase.name}
      </span>
    </div>
  );
}
