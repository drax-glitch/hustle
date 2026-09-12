import React, { useEffect, useState, useCallback } from "react";
import { Map, Swords, Sparkles, Trophy, ArrowRight, Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";
import * as api from "../api/api";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import LoadingState from "../components/LoadingState.jsx";
import EmptyState from "../components/EmptyState.jsx";

const REGION_STAGE_COLORS = {
  unknown: "from-slate-700 to-slate-600",
  discovered: "from-amber-700 to-amber-600",
  explored: "from-emerald-700 to-emerald-600",
  developed: "from-amber-600 to-amber-500",
  mastered: "from-amber-500 to-amber-400",
  legendary: "from-rose-500 to-rose-400",
};

const REGION_STAGE_ICONS = {
  unknown: "🌑",
  discovered: "🌱",
  explored: "🗺️",
  developed: "🏗️",
  mastered: "👑",
  legendary: "✨",
};

const REGION_THEMES = {
  health: {
    border: "border-rose-500/30 hover:border-rose-500/60",
    bg: "bg-gradient-to-br from-ink-900 via-rose-950/15 to-ink-900",
    badge: "text-rose-400 bg-rose-500/15 border-rose-500/30",
    bar: "from-rose-500 to-emerald-400",
  },
  knowledge: {
    border: "border-cyan-500/30 hover:border-cyan-500/60",
    bg: "bg-gradient-to-br from-ink-900 via-cyan-950/15 to-ink-900",
    badge: "text-cyan-400 bg-cyan-500/15 border-cyan-500/30",
    bar: "from-cyan-500 to-blue-400",
  },
  career: {
    border: "border-blue-500/30 hover:border-blue-500/60",
    bg: "bg-gradient-to-br from-ink-900 via-blue-950/15 to-ink-900",
    badge: "text-blue-400 bg-blue-500/15 border-blue-500/30",
    bar: "from-blue-500 to-indigo-400",
  },
  creativity: {
    border: "border-fuchsia-500/30 hover:border-fuchsia-500/60",
    bg: "bg-gradient-to-br from-ink-900 via-fuchsia-950/15 to-ink-900",
    badge: "text-fuchsia-400 bg-fuchsia-500/15 border-fuchsia-500/30",
    bar: "from-fuchsia-500 to-amber-400",
  },
  discipline: {
    border: "border-orange-500/30 hover:border-orange-500/60",
    bg: "bg-gradient-to-br from-ink-900 via-orange-950/15 to-ink-900",
    badge: "text-orange-400 bg-orange-500/15 border-orange-500/30",
    bar: "from-orange-500 to-amber-400",
  },
};

export default function World() {
  const { user } = useApp();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [worldData, setWorldData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await api.fetchWorld();
      setWorldData(data);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load world"), "error");
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) return <LoadingState label="Loading your world realm…" />;
  if (!worldData) return <p className="text-slate-500">Could not load world data.</p>;

  const { regions, worldProgress, activeBosses } = worldData;

  return (
    <div className="space-y-6">
      {/* World Realm Header */}
      <div className="panel p-6 bg-gradient-to-r from-ink-900 via-ink-850 to-ink-900 border border-arcane-500/30 flex items-center justify-between flex-wrap gap-6 shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="font-display text-2xl text-white flex items-center gap-2">
              <Map size={24} className="text-arcane-400" /> The Living Realm
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-arcane-500/20 text-arcane-300 border border-arcane-500/40 font-semibold">
              5 Connected Regions
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Every real-world quest you complete expands territory and fortifies this realm.
          </p>
        </div>
        <div className="flex items-center gap-4 bg-ink-950/80 p-3.5 rounded-2xl border border-ink-700/80 shadow-inner">
          <div className="text-right">
            <p className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Total Realm Mastery</p>
            <p className="text-2xl font-display text-arcane-400 font-bold">{worldProgress}%</p>
          </div>
          <div className="w-36 h-2.5 bg-ink-900 rounded-full overflow-hidden border border-ink-700">
            <div
              className="h-full bg-gradient-to-r from-amber-600 to-amber-400 transition-all duration-500"
              style={{ width: `${worldProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Hero Character Realm Badge */}
      {user && (
        <div className="panel p-4 bg-ink-900/90 border border-ink-800 flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-2xl">
              {user.avatar}
            </div>
            <div>
              <p className="text-sm font-bold text-white">
                {user.displayName} · <span className="text-arcane-400 font-normal">Level {user.level} {user.class?.name || "Adventurer"}</span>
              </p>
              <p className="text-xs text-slate-400">
                {user.evolution ? `${user.evolution.display} (${user.evolution.title})` : "Active Realm Guardian"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate("/boss/create")}
              className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold px-3.5 py-2 rounded-xl transition-colors flex items-center gap-1.5 shadow-sm"
            >
              <Swords size={14} /> Summon New Boss
            </button>
          </div>
        </div>
      )}

      {/* World Map Regions Grid */}
      <div className="panel p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="font-display text-lg text-white">Territory & Region Mastery</h2>
            <p className="text-xs text-slate-400 mt-0.5">Explore each territory to see dedicated quests and boss battles.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {Object.values(regions).map((region) => (
            <RegionCard key={region.id} region={region} onClick={() => navigate(`/world/${region.id}`)} />
          ))}
        </div>
      </div>

      {/* Active Bosses */}
      {activeBosses && activeBosses.length > 0 && (
        <div className="panel p-6 border-2 border-rose-500/30">
          <h2 className="font-display text-lg text-white flex items-center gap-2 mb-4">
            <Swords size={18} className="text-rose-400" /> Active Boss Battles in the Realm
          </h2>
          <div className="space-y-3">
            {activeBosses.map((boss) => (
              <div key={boss.id} className="p-4 rounded-xl bg-ink-800/80 border border-ink-700 flex items-center justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-rose-400 flex items-center justify-center text-2xl shadow-glow">
                    👹
                  </div>
                  <div>
                    <p className="text-white font-bold">{boss.title}</p>
                    <p className="text-xs text-slate-400">{boss.category} Region • {boss.difficulty} Difficulty</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-xs text-slate-400">Phase {boss.currentPhase || 1}</p>
                    <p className="text-sm font-semibold text-rose-400">{boss.hpPercent}% HP</p>
                  </div>
                  <button
                    onClick={() => navigate(`/boss/${boss.id}`)}
                    className="text-xs bg-rose-600 hover:bg-rose-500 text-white font-bold px-4 py-2 rounded-xl transition-colors shadow-glow flex items-center gap-1.5"
                  >
                    <Swords size={14} /> Enter Arena
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {(!activeBosses || activeBosses.length === 0) && (
        <div className="panel p-8 text-center bg-gradient-to-b from-ink-900 to-ink-950 border border-ink-800">
          <Swords size={32} className="text-slate-600 mx-auto mb-3" />
          <p className="text-slate-300 font-semibold mb-1">No Active Boss Battle</p>
          <p className="text-xs text-slate-400 mb-4 max-w-md mx-auto">
            Transform a major life project or milestone into an epic campaign trial.
          </p>
          <button
            onClick={() => navigate("/boss/create")}
            className="bg-arcane-600 hover:bg-arcane-500 text-white text-xs font-semibold px-5 py-2.5 rounded-xl transition-colors shadow-glow inline-flex items-center gap-1.5"
          >
            <Swords size={14} /> Summon Boss
          </button>
        </div>
      )}
    </div>
  );
}

function RegionCard({ region, onClick }) {
  const theme = REGION_THEMES[region.id] || REGION_THEMES.career;
  const stageColor = REGION_STAGE_COLORS[region.stage] || REGION_STAGE_COLORS.unknown;
  const stageIcon = REGION_STAGE_ICONS[region.stage] || REGION_STAGE_ICONS.unknown;

  return (
    <button
      onClick={onClick}
      className={`w-full p-5 rounded-2xl border text-left transition-all duration-200 ${theme.bg} ${theme.border} hover:shadow-lg hover:scale-[1.01]`}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-3xl">{region.icon}</span>
        <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full bg-gradient-to-r ${stageColor} text-white shadow-sm flex items-center gap-1`}>
          {stageIcon} {region.stageDisplay}
        </span>
      </div>
      <h3 className="font-display text-lg text-white font-bold mb-1">{region.name}</h3>
      <p className="text-xs text-slate-400 mb-4 line-clamp-2">{region.description}</p>
      <div className="w-full">
        <div className="flex justify-between text-xs font-semibold mb-1.5">
          <span className="text-slate-400">Territory Control</span>
          <span className="text-white font-mono">{region.progress}%</span>
        </div>
        <div className="h-2.5 bg-ink-950 rounded-full overflow-hidden border border-ink-800">
          <div
            className={`h-full bg-gradient-to-r ${theme.bar} transition-all duration-500`}
            style={{ width: `${region.progress}%` }}
          />
        </div>
      </div>
      <div className="flex items-center justify-between mt-3 text-xs text-slate-400">
        <span>{region.completedQuests} / {region.totalQuests} quests completed</span>
        <span className="text-arcane-400 font-semibold flex items-center gap-1">
          Explore <ArrowRight size={12} />
        </span>
      </div>
    </button>
  );
}

