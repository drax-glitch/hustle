import React from "react";
import { Sparkles, Star, Zap, Crown, Award } from "lucide-react";
import * as api from "../api/api";

export default function LevelUpModal({
  level,
  oldLevel,
  skillPoints,
  goldBonus,
  characterClass,
  evolution,
  onClose,
}) {
  if (!level) return null;

  const levelsGained = level - oldLevel;
  const isMultiLevel = levelsGained > 1;
  const hasEvolved = evolution && (evolution.evolved || evolution.justEvolved);

  const handleClose = async () => {
    if (hasEvolved) {
      try { await api.ackEvolution(); } catch (e) {}
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[90] flex items-center justify-center px-4 bg-black/80 backdrop-blur-sm">
      <div className={`panel bg-ink-900 w-full max-w-md p-8 text-center relative overflow-hidden border-2 ${
        hasEvolved ? "border-amber-500/60" : "border-amber-500/40"
      }`}>
        <div className={`absolute inset-0 bg-gradient-to-b ${
          hasEvolved ? "from-amber-600/15" : "from-amber-600/10"
        } to-transparent pointer-events-none`} />

        <div className="relative">
          {hasEvolved ? (
            <div className="mb-2">
              <span className="text-4xl inline-block mb-1">🧬</span>
              <p className="text-xs uppercase tracking-[0.25em] text-amber-400 font-bold mt-1">Character Evolved!</p>
              <h2 className="font-display text-3xl text-white mt-1 mb-1">{evolution.title || evolution.display}</h2>
              <span className="inline-block text-xs px-3 py-1 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 font-semibold mb-3">
                {evolution.display} Rank
              </span>
            </div>
          ) : (
            <div>
              <Sparkles className="mx-auto text-amber-400 mb-2" size={32} />
              <p className="text-xs uppercase tracking-[0.3em] text-amber-400 font-semibold">Level Up</p>
              {isMultiLevel ? (
                <h2 className="font-display text-4xl text-white mt-2 mb-1">Level {oldLevel} → {level}</h2>
              ) : (
                <h2 className="font-display text-5xl text-white mt-2 mb-1">Level {level}</h2>
              )}
            </div>
          )}

          {characterClass && (
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r ${characterClass.color} text-white font-semibold text-xs mt-1 mb-3 border border-white/15`}>
              <span>{characterClass.icon}</span>
              <span>{characterClass.name}</span>
            </div>
          )}

          <p className="text-sm text-slate-300 mb-5">
            {hasEvolved
              ? `You ascended to the ${evolution.display} stage of power!`
              : isMultiLevel
              ? `You surged ${levelsGained} levels stronger!`
              : "Your power grows with every conquered quest!"}
          </p>

          <div className="space-y-2 text-sm text-slate-300 mb-6 bg-ink-800/80 p-3.5 rounded-xl border border-ink-700/80">
            {skillPoints > 0 && (
              <div className="flex items-center justify-between px-2">
                <span className="text-slate-400 text-xs flex items-center gap-1.5">
                  <Zap size={15} className="text-amber-400" /> Skill Points Awarded
                </span>
                <span className="text-amber-400 font-bold">+{skillPoints} SP</span>
              </div>
            )}
            {goldBonus > 0 && (
              <div className="flex items-center justify-between px-2">
                <span className="text-slate-400 text-xs flex items-center gap-1.5">
                  <Star size={15} className="text-amber-400" /> Level-Up Gold Bonus
                </span>
                <span className="text-amber-400 font-bold">+{goldBonus} Gold</span>
              </div>
            )}
            {hasEvolved && evolution.cosmetics?.unlocked && (
              <div className="pt-2 border-t border-ink-700 text-left">
                <p className="text-[11px] font-semibold text-amber-300 uppercase tracking-wider mb-1 flex items-center gap-1">
                  <Award size={13} className="text-amber-400" /> Unlocked Tier Cosmetics:
                </p>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {evolution.cosmetics.unlocked.map((item) => (
                    <span key={item} className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                      ✨ {item}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <button
            onClick={handleClose}
            className="w-full bg-amber-500 hover:bg-amber-400 transition-colors text-ink-950 font-bold py-3 rounded-xl tracking-wide"
          >
            CONTINUE
          </button>
        </div>
      </div>
    </div>
  );
}
