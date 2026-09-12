import React from "react";
import { Trophy, Sparkles, ArrowRight } from "lucide-react";

export default function BossVictoryModal({ boss, rewards, onClose, onCreateNew }) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center px-4 bg-black/80 backdrop-blur-sm">
      <div className="panel bg-ink-900 w-full max-w-md p-8 text-center border-2 border-emerald-500/50">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-400 flex items-center justify-center text-4xl mx-auto mb-4 shadow-glow animate-pulse">
          🏆
        </div>
        <h2 className="font-display text-2xl text-white mb-2">BOSS DEFEATED</h2>
        <p className="text-slate-400 mb-6">{boss.title} has fallen!</p>

        <div className="bg-ink-800 rounded-xl p-4 mb-6 border border-emerald-500/30">
          <h3 className="text-sm font-semibold text-emerald-400 mb-3 flex items-center justify-center gap-2">
            <Sparkles size={16} /> Victory Rewards
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">XP</span>
              <span className="text-white font-medium">+{rewards.xpReward}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Gold</span>
              <span className="text-white font-medium">+{rewards.goldReward}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Skill Points</span>
              <span className="text-white font-medium">+{rewards.skillPointReward}</span>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-ink-700 hover:bg-ink-600 text-white font-medium py-3 rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            Continue Adventure
            <ArrowRight size={16} />
          </button>
          <button
            onClick={onCreateNew}
            className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-3 rounded-xl transition-colors"
          >
            Create New Boss
          </button>
        </div>
      </div>
    </div>
  );
}
