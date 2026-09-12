import React from "react";
import { CheckCircle, Coins, Zap, Trophy, Skull } from "lucide-react";

export default function RewardPopup({ quest, attributeGains, bossDamage, onClose }) {
  if (!quest) return null;

  return (
    <div className="fixed inset-0 z-[85] flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
      <div className="panel bg-ink-900 w-full max-w-sm p-6 text-center relative">
        <div className="relative">
          <CheckCircle className="mx-auto text-emerald-400 mb-3" size={40} />
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-400 font-semibold mb-2">Quest Complete</p>
          <h3 className="font-display text-xl text-white mb-1">{quest.title}</h3>
          
          <div className="grid grid-cols-2 gap-3 mt-5 mb-5">
            <RewardCard icon={<Zap size={16} className="text-arcane-400" />} label="XP" value={quest.xpReward} />
            <RewardCard icon={<Coins size={16} className="text-amber-400" />} label="Gold" value={quest.goldReward} />
          </div>

          {(() => {
            if (!bossDamage) return null;
            const damageValue = typeof bossDamage === "number" ? bossDamage : bossDamage.damage;
            if (!damageValue || damageValue <= 0) return null;
            const bossTitle = bossDamage.bossTitle;
            const defeated = bossDamage.defeated;

            return (
              <div className="mb-5 p-3 rounded-lg bg-rose-500/15 border border-rose-500/40 animate-pulse">
                <p className="text-xs text-rose-300 uppercase tracking-wide mb-1 flex items-center justify-center gap-1 font-semibold">
                  <Skull size={14} className="text-rose-400" />
                  {bossTitle ? `${bossTitle} Damaged!` : "Boss Damage Dealt"}
                </p>
                <p className="text-xl font-display text-rose-400 font-bold">-{damageValue} HP</p>
                {defeated && (
                  <p className="text-xs text-amber-300 font-bold mt-1 tracking-wider uppercase">
                    👑 BOSS DEFEATED! 👑
                  </p>
                )}
              </div>
            );
          })()}
          
          {attributeGains && Object.keys(attributeGains).length > 0 && (
            <div className="mb-5 p-3 rounded-lg bg-ink-800 border border-ink-700">
              <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Attribute Gains</p>
              {Object.entries(attributeGains).map(([attr, gain]) => (
                <div key={attr} className="flex items-center justify-between text-sm">
                  <span className="text-slate-300">{attr}</span>
                  <span className="text-emerald-400 font-semibold">+{gain}</span>
                </div>
              ))}
            </div>
          )}
          
          <button
            onClick={onClose}
            className="w-full bg-emerald-600 hover:bg-emerald-500 transition-colors text-white font-medium py-2.5 rounded-xl"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}

function RewardCard({ icon, label, value }) {
  return (
    <div className="flex flex-col items-center p-3 rounded-lg bg-ink-800 border border-ink-700">
      {icon}
      <p className="text-xs text-slate-500 mt-1 uppercase tracking-wide">{label}</p>
      <p className="text-lg font-semibold text-slate-100">+{value}</p>
    </div>
  );
}
