import React, { useEffect, useState, useCallback } from "react";
import { Zap, Coins, Flame, ScrollText, Shield, Sparkles } from "lucide-react";
import * as api from "../api/api";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import AttributeBar from "../components/AttributeBar.jsx";
import CharacterEvolution from "../components/CharacterEvolution.jsx";
import LoadingState from "../components/LoadingState.jsx";

const SLOT_ICONS = {
  Avatars: "🧙",
  Weapons: "⚔️",
  Magic: "🛡️",
  Badges: "💍",
  Frames: "🖼️",
  Companions: "🐱",
  Effects: "✨",
};
const DISPLAY_SLOTS = ["Avatars", "Weapons", "Magic", "Badges", "Frames", "Companions", "Effects"];

export default function Character() {
  const { setUser } = useApp();
  const { addToast } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const result = await api.fetchCharacter();
      setData(result);
      if (result.user) setUser(result.user);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load character"), "error");
    } finally {
      setLoading(false);
    }
  }, [addToast, setUser]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) return <LoadingState label="Loading character sheet…" />;
  if (!data) return <p className="text-slate-500">Could not load character.</p>;

  const { user, attributes, equipped, class: characterClass, evolution, skills } = data;
  const equippedBySlot = Object.fromEntries(equipped.map((e) => [e.category, e]));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <span className="eyebrow-amber">YOUR CHARACTER</span>
        <h1 className="font-display text-3xl font-bold text-white tracking-tight mt-1">Character Sheet</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Avatar Profile Card */}
        <div className="lg:col-span-6 space-y-6">
          <div className="panel p-6 sm:p-8 bg-ink-900 border border-ink-800">
            <div className="flex flex-col items-center text-center">
              <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-ink-850 border-2 border-arcane-500/40 flex items-center justify-center text-5xl sm:text-6xl mb-4 shadow-lg">
                {user.avatar || "🧙"}
              </div>
              <h2 className="font-display text-2xl font-bold text-white tracking-tight">{user.displayName}</h2>
              
              {/* Character Class Display */}
              {characterClass && (
                <div className="mt-2 px-3 py-1 rounded-full bg-ink-800 text-slate-200 font-semibold text-xs border border-ink-700 flex items-center gap-1.5">
                  <span>{characterClass.icon}</span>
                  <span>{characterClass.name}</span>
                </div>
              )}
              
              <p className="text-xs text-arcane-400 font-mono mt-1">{evolution?.title || user.title}</p>

              <div className="w-full mt-5">
                <div className="flex justify-between text-xs text-slate-400 mb-1.5 font-mono">
                  <span>LVL {user.level}</span>
                  <span>{user.xp} / {user.xpToNext} XP</span>
                </div>
                <div className="progress-track h-2 bg-ink-800">
                  <div
                    className="progress-fill bg-gradient-to-r from-arcane-500 to-amber-300"
                    style={{ width: `${(user.xp / user.xpToNext) * 100}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 w-full mt-6">
                <StatBox icon={<Zap size={14} className="text-arcane-400" />} value={`LVL ${user.level}`} label="Rank" />
                <StatBox icon={<Coins size={14} className="text-arcane-400" />} value={user.gold.toLocaleString()} label="Gold" />
                <StatBox icon={<Flame size={14} className="text-amber-400" />} value={`${user.streak}d`} label="Streak" />
                <StatBox icon={<ScrollText size={14} className="text-emerald-400" />} value={user.questsDone} label="Quests" />
              </div>
              {user.skillPoints > 0 && (
                <p className="text-xs text-arcane-400 font-mono mt-4">
                  ★ {user.skillPoints} Skill Points Available for Mastery
                </p>
              )}
            </div>
          </div>

          {/* Character Class Lore */}
          {characterClass && (
            <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
              <span className="eyebrow-amber flex items-center gap-1.5 mb-2">
                <span>{characterClass.icon}</span> Class Archetype
              </span>
              <h3 className="font-display text-lg font-bold text-white mb-1.5">{characterClass.name}</h3>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">{characterClass.description}</p>
            </div>
          )}
        </div>

        {/* Right Column: Evolution, Attributes & Skills */}
        <div className="lg:col-span-6 space-y-6">
          {/* Character Evolution Tier */}
          <CharacterEvolution evolution={evolution} />

          {/* Core Attributes */}
          <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
            <span className="eyebrow-amber flex items-center gap-1.5 mb-4">
              <Zap size={13} className="text-arcane-400" /> Core Attributes
            </span>
            {Object.entries(attributes).map(([key, data]) => (
              <AttributeBar key={key} name={key} value={data.value} tier={data.tier} />
            ))}
          </div>

          {/* Skills Section */}
          <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
            <span className="eyebrow-amber flex items-center gap-1.5 mb-4">
              <Sparkles size={13} className="text-arcane-400" /> Unlocked Skills
            </span>
            {skills.length > 0 ? (
              <div className="space-y-2.5">
                {skills.map((skill) => (
                  <div key={skill.id} className="p-3 rounded-lg bg-ink-850 border border-ink-750 flex items-center gap-3">
                    <span className="text-2xl shrink-0">{skill.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-slate-200 font-semibold text-xs truncate">{skill.name}</p>
                      <p className="text-slate-400 text-[11px] truncate">{skill.description}</p>
                    </div>
                    <span className="text-[10px] font-mono font-semibold uppercase px-2 py-0.5 rounded bg-ink-900 border border-ink-700 text-arcane-400 shrink-0">
                      {skill.attribute}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 text-center py-4">
                No skills unlocked yet. Complete quests and level up to earn Skill Points!
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Equipment Arsenal */}
      <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
        <div className="flex items-center justify-between mb-4">
          <span className="eyebrow-amber flex items-center gap-1.5">
            <Shield size={13} className="text-arcane-400" /> Equipped Items
          </span>
          <span className="text-[11px] text-slate-400 font-mono">
            Equip cosmetics from the Shop
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
          {DISPLAY_SLOTS.map((slot) => {
            const item = equippedBySlot[slot];
            return (
              <div
                key={slot}
                className={`aspect-square rounded-lg border flex flex-col items-center justify-center gap-1 p-2 text-center transition-colors ${
                  item ? "bg-ink-850 border-arcane-500/40" : "bg-ink-900 border-ink-800 text-slate-600"
                }`}
              >
                <span className="text-2xl">{item ? item.icon : SLOT_ICONS[slot]}</span>
                <span className="text-[10px] text-slate-300 font-medium truncate w-full px-1">{item ? item.name : "Empty"}</span>
                <span className="text-[9px] uppercase tracking-wider text-slate-500 font-mono">{slot}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function StatBox({ icon, value, label }) {
  return (
    <div className="bg-ink-850 border border-ink-750 rounded-lg p-2.5 flex flex-col items-center text-center">
      {icon}
      <p className="text-xs font-bold text-slate-100 font-mono mt-1">{value}</p>
      <p className="text-[9px] text-slate-400 uppercase tracking-wider font-semibold">{label}</p>
    </div>
  );
}

