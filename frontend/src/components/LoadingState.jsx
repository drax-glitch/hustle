import React from "react";
import { Sparkles } from "lucide-react";

export default function LoadingState({ label = "Loading…" }) {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="flex items-center gap-2 text-slate-400 mb-6">
        <Sparkles className="text-arcane-400 animate-spin" size={18} />
        <span className="text-sm">{label}</span>
      </div>
      <div className="panel p-6 h-24 bg-ink-800/50" />
      <div className="panel p-6 h-48 bg-ink-800/50" />
      <div className="grid grid-cols-2 gap-4">
        <div className="panel p-4 h-20 bg-ink-800/50" />
        <div className="panel p-4 h-20 bg-ink-800/50" />
      </div>
    </div>
  );
}
