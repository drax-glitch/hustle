import React, { useEffect, useState, useCallback } from "react";
import { Lock, Unlock, Zap, Sparkles } from "lucide-react";
import * as api from "../api/api";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import LoadingState from "../components/LoadingState.jsx";

const ATTRIBUTE_ICONS = {
  Strength: "💪",
  Intelligence: "🧠",
  Discipline: "🔥",
  Creativity: "🎨",
  Vitality: "❤️",
};

export default function Skills() {
  const { user, setUser } = useApp();
  const { addToast } = useToast();
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    try {
      const data = await api.fetchSkills();
      setSkills(data);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load skills"), "error");
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    load();
  }, [load]);

  const handleUnlock = async (skill) => {
    setBusyId(skill.id);
    try {
      const result = await api.unlockSkill(skill.id);
      if (result.user) setUser(result.user);
      addToast(`Unlocked ${skill.name}!`, "success");
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to unlock skill"), "error");
    } finally {
      setBusyId(null);
    }
  };

  // Group skills by attribute
  const skillsByAttribute = skills.reduce((acc, skill) => {
    if (!acc[skill.attribute]) acc[skill.attribute] = [];
    acc[skill.attribute].push(skill);
    return acc;
  }, {});

  if (loading) return <LoadingState label="Studying the ancient grimoire…" />;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <span className="eyebrow-amber">CHARACTER PROFICIENCY</span>
          <h1 className="font-display text-3xl font-bold text-white tracking-tight mt-1">Abilities & Skill Tree</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">Unlock active masteries using earned Skill Points to empower your journey.</p>
        </div>
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-ink-900 border border-ink-700/80 text-arcane-400 font-mono font-bold text-sm">
          <Zap size={15} /> {user.skillPoints} Skill Points Available
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(skillsByAttribute).map(([attribute, attrSkills]) => (
          <section key={attribute} className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
            <div className="flex items-center gap-2 mb-4 pb-2.5 border-b border-ink-800">
              <span className="text-lg">{ATTRIBUTE_ICONS[attribute]}</span>
              <span className="eyebrow-amber">{attribute} Mastery</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {attrSkills.map((skill) => (
                <SkillCard
                  key={skill.id}
                  skill={skill}
                  onUnlock={handleUnlock}
                  busyId={busyId}
                  skillPoints={user.skillPoints}
                />
              ))}
            </div>
          </section>
        ))}
      </div>

      {skills.length === 0 && (
        <div className="panel p-10 text-center bg-ink-900 border border-ink-800">
          <p className="text-slate-400 text-sm">No skills available yet. Conquer directives and level up to earn Skill Points!</p>
        </div>
      )}
    </div>
  );
}

function SkillCard({ skill, onUnlock, busyId, skillPoints }) {
  const canUnlock = !skill.unlocked && skillPoints >= skill.cost && (!skill.prerequisite || skill.prerequisite.unlocked);
  const isBusy = busyId === skill.id;

  return (
    <div className={`p-4 rounded-lg border flex items-center justify-between gap-3.5 transition-colors ${
      skill.unlocked
        ? "bg-ink-850 border-emerald-500/30"
        : canUnlock
        ? "bg-ink-850 border-ink-750 hover:border-arcane-500/50"
        : "bg-ink-900/60 border-ink-800/80 opacity-50"
    }`}>
      <div className="flex items-center gap-3.5 min-w-0 flex-1">
        <div className="w-10 h-10 rounded-lg bg-ink-900 border border-ink-750 flex items-center justify-center text-xl shrink-0">
          {skill.icon}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <h3 className={`font-semibold text-xs sm:text-sm truncate ${skill.unlocked ? "text-emerald-400" : "text-slate-200"}`}>
              {skill.name}
            </h3>
            {skill.unlocked ? (
              <Unlock size={12} className="text-emerald-400 shrink-0" />
            ) : (
              <Lock size={12} className="text-slate-500 shrink-0" />
            )}
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{skill.description}</p>
          <div className="flex items-center gap-2.5 mt-1.5 text-[10px] font-mono">
            <span className="text-arcane-400 font-bold">{skill.cost} SP</span>
            {skill.prerequisite && (
              <span className="text-slate-400 truncate">
                Req: {skill.prerequisite.name} {skill.prerequisite.unlocked ? "✓" : "🔒"}
              </span>
            )}
          </div>
        </div>
      </div>
      {!skill.unlocked && (
        <button
          disabled={!canUnlock || isBusy}
          onClick={() => onUnlock(skill)}
          className={`text-xs font-bold px-3 py-1.5 rounded-md transition-colors shrink-0 shadow-sm ${
            canUnlock
              ? "bg-arcane-500 hover:bg-arcane-400 text-ink-950"
              : "bg-ink-800 text-slate-500 cursor-not-allowed border border-ink-700"
          } disabled:opacity-50`}
        >
          {isBusy ? "..." : "Master"}
        </button>
      )}
    </div>
  );
}