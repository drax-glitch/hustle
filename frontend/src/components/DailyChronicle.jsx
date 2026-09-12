import React, { useState, useEffect } from "react";
import { Scroll, Calendar, BookOpen, ChevronDown, ChevronUp, Sparkles, Swords, Trophy } from "lucide-react";
import * as api from "../api/api";
import { useToast } from "../context/ToastContext.jsx";

export default function DailyChronicle({ isPreview = false, maxItems = 3 }) {
  const { addToast } = useToast();
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedDay, setExpandedDay] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.fetchChronicleHistory(isPreview ? 7 : 30);
      setHistory(data);
      if (data && data.length > 0 && data[0].hasActivity) {
        setExpandedDay(data[0].date);
      }
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load chronicle"), "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div className="panel p-5 bg-ink-900 border border-ink-800">
        <div className="flex items-center gap-3 animate-pulse">
          <div className="w-8 h-8 rounded bg-ink-800" />
          <div className="space-y-1.5 flex-1">
            <div className="h-3 bg-ink-800 rounded w-1/4" />
            <div className="h-2.5 bg-ink-800 rounded w-1/3" />
          </div>
        </div>
      </div>
    );
  }

  if (!history) {
    return (
      <div className="panel p-5 text-center text-slate-500">
        <p>Could not load chronicle.</p>
      </div>
    );
  }

  const displayHistory = isPreview ? history.slice(0, maxItems) : history;

  return (
    <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="eyebrow-amber flex items-center gap-1.5">
            <Scroll size={13} className="text-arcane-400" /> {isPreview ? "Today's Chronicle" : "Daily Chronicle"}
          </span>
        </div>
        <button
          onClick={load}
          className="p-1 text-slate-400 hover:text-white transition-colors"
          title="Refresh Chronicle"
        >
          <Calendar size={14} />
        </button>
      </div>

      {displayHistory.length === 0 ? (
        <div className="text-center py-6 border border-dashed border-ink-800 rounded-lg">
          <BookOpen size={24} className="text-slate-600 mx-auto mb-2" />
          <p className="text-slate-400 text-xs font-medium">No chronicle entries yet.</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Complete quests and battle bosses to forge your journal.</p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {displayHistory.map((entry) => (
            <ChronicleEntry
              key={entry.date}
              entry={entry}
              isExpanded={expandedDay === entry.date}
              onToggle={() => setExpandedDay(expandedDay === entry.date ? null : entry.date)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ChronicleEntry({ entry, isExpanded, onToggle }) {
  const { date, title, stats, quests, bossActivity, levelUps, skills, achievements } = entry;
  const attributeGains = stats?.attributeGains || {};
  const hasAttributeGains = Object.keys(attributeGains).length > 0;

  const formattedDate = new Date(date).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  return (
    <div className={`border rounded-lg overflow-hidden transition-all duration-150 ${
      isExpanded ? "border-arcane-500/40 bg-ink-850" : "border-ink-800 bg-ink-900 hover:border-ink-700"
    }`}>
      <button
        onClick={onToggle}
        className="w-full p-3.5 flex items-center justify-between text-left transition-colors"
      >
        <div className="flex-1 min-w-0 pr-3">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-[10px] font-mono uppercase tracking-wider text-arcane-400/90 font-semibold">{formattedDate}</span>
            {stats.bossDefeated > 0 && (
              <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                DEFEATED BOSS
              </span>
            )}
            {stats.levelUps > 0 && (
              <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                ASCENDED
              </span>
            )}
          </div>
          <p className="text-white font-medium text-sm truncate">{title}</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="hidden sm:flex items-center gap-2.5 text-slate-400 text-[11px] font-mono">
            <span>{stats.questsCompleted} quests</span>
            <span className="text-arcane-400 font-semibold">+{stats.xpGained} XP</span>
          </div>
          <div className="text-slate-400">
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </div>
        </div>
      </button>

      {isExpanded && (
        <div className="p-3.5 bg-ink-950/80 border-t border-ink-800 space-y-3 text-xs">
          {/* Stat Pillars */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-2 rounded bg-ink-900 border border-ink-800 text-center">
              <p className="text-[9px] uppercase tracking-wider text-slate-400">Quests</p>
              <p className="text-white font-bold text-sm font-mono">{stats.questsCompleted}</p>
            </div>
            <div className="p-2 rounded bg-ink-900 border border-ink-800 text-center">
              <p className="text-[9px] uppercase tracking-wider text-slate-400">XP Earned</p>
              <p className="text-arcane-400 font-bold text-sm font-mono">+{stats.xpGained}</p>
            </div>
            <div className="p-2 rounded bg-ink-900 border border-ink-800 text-center">
              <p className="text-[9px] uppercase tracking-wider text-slate-400">Gold</p>
              <p className="text-amber-400 font-bold text-sm font-mono">+{stats.goldGained}</p>
            </div>
            <div className="p-2 rounded bg-ink-900 border border-ink-800 text-center">
              <p className="text-[9px] uppercase tracking-wider text-slate-400">Boss Damage</p>
              <p className="text-rose-400 font-bold text-sm font-mono">{stats.bossDamage > 0 ? `-${stats.bossDamage}` : stats.bossDefeated > 0 ? "VICTORY" : "0"}</p>
            </div>
          </div>

          {/* Attribute Growth */}
          {hasAttributeGains && (
            <div className="p-2.5 rounded bg-ink-900 border border-ink-800">
              <p className="text-[10px] text-slate-400 uppercase tracking-wide font-semibold mb-1.5 flex items-center gap-1">
                <Sparkles size={11} className="text-arcane-400" /> Attributes Honed
              </p>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(attributeGains).map(([attr, gain]) => (
                  <span
                    key={attr}
                    className="px-2 py-0.5 rounded bg-ink-850 border border-ink-750 text-[11px] text-slate-200"
                  >
                    {attr.toUpperCase()} <span className="text-emerald-400 font-semibold font-mono">+{gain}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Milestones */}
          {(levelUps?.length > 0 || skills?.length > 0 || achievements?.length > 0) && (
            <div className="p-2.5 rounded bg-ink-900 border border-ink-800 space-y-1.5">
              <p className="text-[10px] text-slate-400 uppercase tracking-wide font-semibold flex items-center gap-1">
                <Trophy size={11} className="text-arcane-400" /> Milestones & Feats
              </p>
              <div className="flex flex-wrap gap-1.5">
                {levelUps?.map((lvl, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px] font-medium">
                    ⭐ Level {lvl.level || lvl.new_level}
                  </span>
                ))}
                {skills?.map((sk, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-arcane-500/10 text-arcane-400 border border-arcane-500/30 text-[11px] font-medium">
                    ✨ {sk.name || "Skill"}
                  </span>
                ))}
                {achievements?.map((ach, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[11px] font-medium">
                    🏆 {ach.title || "Achievement"}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Quests Summary */}
          {quests && quests.length > 0 && (
            <div>
              <p className="text-[10px] text-slate-400 uppercase tracking-wide font-semibold mb-1.5">Conquered Directives</p>
              <div className="space-y-1">
                {quests.map((quest) => (
                  <div key={quest.id} className="p-2 rounded bg-ink-900 border border-ink-800/80 flex items-center justify-between">
                    <div>
                      <p className="text-slate-200 text-xs font-medium">{quest.title}</p>
                      <p className="text-[10px] text-slate-400 capitalize">{quest.category} • {quest.difficulty}</p>
                    </div>
                    <div className="text-right text-[11px] font-mono text-arcane-400 font-semibold">
                      +{quest.xpReward} XP
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Boss Battles */}
          {bossActivity && (bossActivity.defeatedBosses?.length > 0 || bossActivity.damageEvents?.length > 0) && (
            <div>
              <p className="text-[10px] text-slate-400 uppercase tracking-wide font-semibold mb-1.5 flex items-center gap-1">
                <Swords size={11} className="text-rose-400" /> Boss Engagements
              </p>
              <div className="space-y-1">
                {bossActivity.defeatedBosses?.map((boss, idx) => (
                  <div key={`def-${boss.id || idx}`} className="p-2 rounded bg-rose-500/10 border border-rose-500/30 flex items-center justify-between">
                    <div>
                      <p className="text-rose-400 text-xs font-semibold">🏆 Defeated: {boss.title}</p>
                    </div>
                    <span className="text-[10px] font-bold text-rose-300 uppercase px-1.5 py-0.2 rounded bg-rose-500/20">Defeated</span>
                  </div>
                ))}
                {bossActivity.damageEvents?.map((dmg, idx) => (
                  <div key={`dmg-${idx}`} className="p-1.5 rounded bg-ink-900 border border-ink-800 flex items-center justify-between text-[11px] font-mono">
                    <span className="text-slate-400">Struck {dmg.bossTitle || "Boss"}</span>
                    <span className="text-rose-400 font-bold">-{dmg.damage} HP</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


