import React, { useEffect, useState, useCallback } from "react";
import { Coins, Flame, CheckSquare, Plus, Zap, Trophy, Target, Swords, Map, ArrowRight, Sparkles, Shield, Compass, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import * as api from "../api/api";
import { useQuestCompletion } from "../hooks/useQuestCompletion.js";
import QuestCard from "../components/QuestCard.jsx";
import AttributeBar from "../components/AttributeBar.jsx";
import StatPill from "../components/StatPill.jsx";
import LoadingState from "../components/LoadingState.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LevelUpModal from "../components/LevelUpModal.jsx";
import RewardPopup from "../components/RewardPopup.jsx";
import QuestDamageAnimation from "../components/QuestDamageAnimation.jsx";
import GameMaster from "../components/GameMaster.jsx";
import CharacterEvolution from "../components/CharacterEvolution.jsx";
import DailyChronicle from "../components/DailyChronicle.jsx";

const CATEGORIES = ["Work", "Learning", "Health", "Creative", "Wellness"];
const DIFFICULTIES = ["EASY", "MEDIUM", "HARD"];

export default function Dashboard() {
  const { user, setUser } = useApp();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [quests, setQuests] = useState([]);
  const [stats, setStats] = useState(null);
  const [attributes, setAttributes] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [activeBoss, setActiveBoss] = useState(null);
  const [worldData, setWorldData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterTab, setFilterTab] = useState("ACTIVE");
  const [todoTitle, setTodoTitle] = useState("");
  const [todoCategory, setTodoCategory] = useState("Work");
  const [todoDifficulty, setTodoDifficulty] = useState("EASY");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  const { levelUp, bossDamage, rewardPopup, dismissLevelUp, dismissBossDamage, dismissRewardPopup } = useQuestCompletion();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [questData, statsData, charData, bossData, worldRes] = await Promise.all([
        api.fetchQuests(),
        api.fetchDashboardStats(),
        api.fetchCharacter(),
        api.fetchBosses(),
        api.fetchWorld().catch(() => null),
      ]);
      setQuests(questData);
      setStats(statsData);
      setAttributes(charData.attributes);
      setAchievements(statsData.achievements || []);
      setUser(charData.user);
      if (worldRes) setWorldData(worldRes);
      
      // Boss binding
      if (Array.isArray(bossData)) {
        setActiveBoss(bossData.find((b) => b.status === "active") || null);
      } else if (bossData?.active_boss) {
        setActiveBoss(bossData.active_boss);
      } else {
        setActiveBoss(null);
      }
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load dashboard"), "error");
    } finally {
      setLoading(false);
    }
  }, [addToast, setUser]);

  useEffect(() => {
    load();
  }, [load]);

  const handleAddTodo = async (e) => {
    e.preventDefault();
    if (!todoTitle.trim() || isSubmitting) return;
    setIsSubmitting(true);
    try {
      const newQuest = await api.createQuest({
        title: todoTitle,
        category: todoCategory,
        difficulty: todoDifficulty,
      });
      setQuests((prev) => [newQuest, ...prev]);
      setTodoTitle("");
      addToast("Directive inscribed! Ready to conquer.", "success");
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to create quest"), "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleComplete = async (id) => {
    try {
      const updated = await api.completeQuest(id);
      setQuests((prev) => prev.map((q) => (q.id === id ? updated : q)));
      load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to complete quest"), "error");
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteQuest(id);
      setQuests((prev) => prev.filter((q) => q.id !== id));
      addToast("Quest removed from log", "success");
      setDeleteConfirmId(null);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to delete quest"), "error");
    }
  };

  const confirmDelete = () => {
    if (deleteConfirmId) handleDelete(deleteConfirmId);
  };

  const activeQuests = quests.filter((q) => q.status === "ACTIVE");
  const filteredQuests = quests.filter((q) => {
    if (filterTab === "ACTIVE") return q.status === "ACTIVE";
    if (filterTab === "COMPLETED") return q.status === "COMPLETED";
    return true;
  });

  const dailyGoal = stats?.dailyGoal || user?.dailyGoal || 5;
  const completedToday = stats?.completedToday ?? 0;
  const remainingToday = stats?.remainingToday ?? dailyGoal;
  const dailyPct = Math.min(100, Math.round((completedToday / dailyGoal) * 100));

  if (loading) return <LoadingState label="Loading your world…" />;

  const evolution = user?.evolution;

  return (
    <div className="space-y-8">
      {levelUp && (
        <LevelUpModal
          level={levelUp.level}
          oldLevel={levelUp.oldLevel}
          skillPoints={levelUp.skillPoints}
          goldBonus={levelUp.goldBonus}
          characterClass={levelUp.characterClass}
          evolution={levelUp.evolution}
          onClose={dismissLevelUp}
        />
      )}
      {rewardPopup && (
        <RewardPopup
          quest={rewardPopup.quest}
          attributeGains={rewardPopup.attributeGains}
          bossDamage={rewardPopup.bossDamage}
          onClose={dismissRewardPopup}
        />
      )}
      {bossDamage && (
        <QuestDamageAnimation
          damage={bossDamage.damage}
          isCritical={bossDamage.isCritical}
          onClose={dismissBossDamage}
        />
      )}

      {/* 1. HERO / PLAYER IDENTITY */}
      {user && (
        <section className="panel p-6 sm:p-8 bg-gradient-to-br from-ink-900 via-ink-900 to-ink-950 border border-ink-800 relative overflow-hidden">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
            {/* Player Identity Details */}
            <div className="flex items-center gap-5 sm:gap-6">
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-ink-850 border-2 border-arcane-500/40 flex items-center justify-center text-4xl sm:text-5xl shrink-0 shadow-lg">
                {user.avatar || "🧙"}
              </div>
              <div className="space-y-1.5">
                <div className="flex items-center gap-2.5 flex-wrap">
                  <span className="eyebrow-amber">YOUR HUSTLE</span>
                  <span className="text-slate-600">·</span>
                  <span className="text-xs font-mono font-bold text-arcane-400">
                    LEVEL {user.level}
                  </span>
                  {user.class && (
                    <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-ink-800 text-slate-200 border border-ink-700">
                      {user.class.icon} {user.class.name}
                    </span>
                  )}
                  {evolution && (
                    <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-arcane-500/15 text-arcane-300 border border-arcane-500/30">
                      {evolution.title}
                    </span>
                  )}
                </div>

                <h1 className="text-2xl sm:text-3xl lg:text-4xl font-display font-bold text-white tracking-tight">
                  {user.displayName}
                </h1>

                <p className="text-xs sm:text-sm text-slate-400 font-light italic">
                  "Build the life you want to live. Every action shapes your domain."
                </p>

                {/* Level XP Bar */}
                <div className="flex items-center gap-3 pt-1.5 w-full max-w-sm">
                  <span className="text-[11px] text-arcane-400 font-mono font-bold">LVL {user.level}</span>
                  <div className="progress-track flex-1 h-1.5 bg-ink-800">
                    <div
                      className="progress-fill bg-gradient-to-r from-arcane-500 to-amber-300"
                      style={{ width: `${Math.min(100, (user.xp / user.xpToNext) * 100)}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">{user.xp} / {user.xpToNext} XP</span>
                </div>
              </div>
            </div>

            {/* Stat Pill Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:flex lg:flex-wrap gap-2 w-full lg:w-auto pt-4 lg:pt-0 border-t lg:border-t-0 border-ink-800">
              <StatPill icon={<Flame size={14} />} value={`${user.streak || 0}d`} label="Streak" color="text-amber-400" />
              <StatPill icon={<Coins size={14} />} value={user.gold?.toLocaleString() || "0"} label="Gold" color="text-arcane-400" />
              <StatPill icon={<Zap size={14} />} value={`+${stats?.todayXp || 0}`} label="Today's XP" color="text-slate-200" />
              <StatPill icon={<CheckSquare size={14} />} value={`${activeQuests.length}`} label="Directives" color="text-emerald-400" />
            </div>
          </div>
        </section>
      )}

      {/* 2. ACTIVE BOSS / ADVENTURE FEATURE */}
      {activeBoss ? (
        <section className="panel p-6 sm:p-8 bg-gradient-to-r from-ink-900 via-rose-950/20 to-ink-900 border border-rose-500/40 relative overflow-hidden">
          <div className="flex items-center justify-between flex-wrap gap-4 mb-4">
            <div className="flex items-center gap-2">
              <span className="eyebrow-crimson flex items-center gap-1.5">
                <Swords size={13} className="text-rose-400" /> Active Boss Battle
              </span>
              <span className="text-slate-600">·</span>
              <span className="text-xs font-mono text-slate-400">Phase {activeBoss.currentPhase} — {activeBoss.phaseName}</span>
            </div>
            <button
              onClick={() => navigate(`/boss/${activeBoss.id}`)}
              className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5 shadow-sm"
            >
              <Swords size={13} /> Enter Arena <ArrowRight size={13} />
            </button>
          </div>

          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-xl bg-ink-850 border border-rose-500/30 flex items-center justify-center text-3xl shrink-0">
                👹
              </div>
              <div>
                <h2 className="text-xl sm:text-2xl font-display font-bold text-white tracking-tight">
                  {activeBoss.title}
                </h2>
                <p className="text-xs text-slate-400 capitalize mt-0.5">
                  {activeBoss.category} Region Boss · {activeBoss.difficulty} Trial
                </p>
              </div>
            </div>

            <div className="w-full md:w-80 max-w-full">
              <div className="flex justify-between text-xs font-semibold mb-1.5">
                <span className="text-slate-400">Boss Integrity</span>
                <span className="text-rose-400 font-mono">
                  {activeBoss.currentHp.toLocaleString()} / {activeBoss.maxHp.toLocaleString()} HP ({activeBoss.hpPercent}%)
                </span>
              </div>
              <div className="progress-track h-2.5 bg-ink-950 border border-ink-800">
                <div
                  className="progress-fill bg-gradient-to-r from-rose-500 to-rose-400"
                  style={{ width: `${activeBoss.hpPercent}%` }}
                />
              </div>
            </div>
          </div>
        </section>
      ) : (
        <section className="panel p-5 bg-ink-900 border border-ink-800 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-ink-850 border border-ink-750 flex items-center justify-center text-xl text-slate-400">
              ⚔️
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-200">No active campaign trial</p>
              <p className="text-xs text-slate-400">Transform a major real-life milestone into an epic boss battle.</p>
            </div>
          </div>
          <button
            onClick={() => navigate("/boss/create")}
            className="bg-ink-800 hover:bg-ink-750 text-arcane-400 text-xs font-semibold px-4 py-2 rounded-lg border border-arcane-500/30 transition-colors flex items-center gap-1.5"
          >
            <Plus size={14} /> Summon Boss
          </button>
        </section>
      )}

      {/* 3. GAME MASTER TACTICIAN */}
      <GameMaster />

      {/* 4. MAIN ASYMMETRIC CONTENT GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (7 cols): Directives & Quests */}
        <div className="lg:col-span-7 space-y-6">
          {/* Daily Goal Directives Bar */}
          <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
            <div className="flex items-center justify-between flex-wrap gap-3 mb-3">
              <span className="eyebrow-amber flex items-center gap-1.5">
                <Target size={13} className="text-arcane-400" /> Daily Directives
              </span>
              {stats?.dailyGoalComplete && (
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold">
                  ✓ Daily Quota Reached
                </span>
              )}
            </div>
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-slate-300 text-xs">
                <span className="font-bold text-white font-mono text-sm">{completedToday}</span> of {dailyGoal} directives conquered today
              </span>
              <span className="text-slate-400 text-xs font-mono">
                {remainingToday > 0 ? `${remainingToday} remaining` : "Goal achieved!"}
              </span>
            </div>
            <div className="progress-track h-2 bg-ink-800">
              <div
                className="progress-fill bg-gradient-to-r from-emerald-500 to-arcane-400"
                style={{ width: `${dailyPct}%` }}
              />
            </div>
            {stats && (
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Lifetime: {stats.totalCompleted} quests conquered · +{stats.todayGold || 0} gold earned today
              </p>
            )}
          </div>

          {/* Quick Inscribe Directive */}
          <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
            <span className="eyebrow-amber flex items-center gap-1.5 mb-3">
              <Plus size={13} className="text-arcane-400" /> Inscribe Directive
            </span>
            <form onSubmit={handleAddTodo} className="space-y-3">
              <div className="flex gap-2 flex-col sm:flex-row">
                <input
                  type="text"
                  placeholder="What real-world quest will you conquer today?"
                  value={todoTitle}
                  onChange={(e) => setTodoTitle(e.target.value)}
                  className="flex-1 bg-ink-850 border border-ink-750 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-arcane-500 transition-colors"
                />
                <button
                  type="submit"
                  disabled={!todoTitle.trim() || isSubmitting}
                  className="bg-arcane-500 hover:bg-arcane-400 disabled:opacity-50 text-ink-950 text-xs font-bold px-4 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-colors shrink-0 shadow-sm"
                >
                  <Plus size={14} /> Add Directive
                </button>
              </div>
              <div className="flex items-center gap-2 flex-wrap text-xs text-slate-400">
                <select
                  value={todoCategory}
                  onChange={(e) => setTodoCategory(e.target.value)}
                  className="bg-ink-850 border border-ink-750 rounded-md px-2.5 py-1 text-xs text-slate-200"
                >
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
                <select
                  value={todoDifficulty}
                  onChange={(e) => setTodoDifficulty(e.target.value)}
                  className="bg-ink-850 border border-ink-750 rounded-md px-2.5 py-1 text-xs text-slate-200"
                >
                  {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
            </form>
          </div>

          {/* Active Quest Log */}
          <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
            <div className="flex items-center justify-between flex-wrap gap-4 mb-4 pb-3 border-b border-ink-800">
              <div>
                <span className="eyebrow-amber">QUEST LOG</span>
                <p className="text-xs text-slate-400 mt-0.5">
                  {activeQuests.length} active directives · {completedToday} conquered today
                </p>
              </div>
              <div className="flex items-center gap-1 bg-ink-850 p-1 rounded-lg border border-ink-750">
                {["ACTIVE", "COMPLETED", "ALL"].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setFilterTab(tab)}
                    className={`text-xs px-2.5 py-1 rounded font-medium transition-colors ${
                      filterTab === tab ? "bg-ink-750 text-arcane-400 font-semibold" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {tab === "ACTIVE" ? `Active (${activeQuests.length})` :
                     tab === "COMPLETED" ? "Completed" : "All"}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2.5">
              {filteredQuests.map((q) => (
                <QuestCard
                  key={q.id}
                  quest={q}
                  onComplete={handleComplete}
                  onDelete={handleDelete}
                  activeBoss={activeBoss}
                />
              ))}
              {filteredQuests.length === 0 && (
                <EmptyState
                  message={
                    filterTab === "ACTIVE"
                      ? "All active quests conquered! Inscribe a new directive to continue your journey."
                      : filterTab === "COMPLETED"
                      ? "No completed quests recorded yet."
                      : "No quests found in log."
                  }
                />
              )}
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): Player Domain, Progression & World */}
        <div className="lg:col-span-5 space-y-6">
          {/* Character Evolution Tier */}
          <CharacterEvolution evolution={user?.evolution} />

          {/* World Progress Realm Snapshot */}
          {worldData && (
            <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
              <div className="flex items-center justify-between mb-3">
                <span className="eyebrow-amber flex items-center gap-1.5">
                  <Map size={13} className="text-arcane-400" /> World Territories
                </span>
                <span className="text-xs font-mono font-bold text-arcane-400">{worldData.worldProgress}% Unlocked</span>
              </div>
              <div className="progress-track h-1.5 bg-ink-800 mb-4">
                <div
                  className="progress-fill bg-gradient-to-r from-arcane-500 to-amber-300"
                  style={{ width: `${worldData.worldProgress}%` }}
                />
              </div>
              <div className="grid grid-cols-5 gap-1.5 text-center">
                {Object.values(worldData.regions || {}).map((r) => (
                  <button
                    key={r.id}
                    onClick={() => navigate(`/world/${r.id}`)}
                    className="p-2 rounded-lg bg-ink-850 hover:bg-ink-800 border border-ink-750 text-center transition-colors"
                    title={`${r.name}: ${r.progress}% (${r.stageDisplay})`}
                  >
                    <span className="text-lg block">{r.icon}</span>
                    <span className="text-[10px] text-slate-300 font-mono font-bold block truncate">{r.progress}%</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Daily Chronicle Preview */}
          <DailyChronicle isPreview={true} maxItems={2} />

          {/* Core Attributes */}
          <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
            <span className="eyebrow-amber flex items-center gap-1.5 mb-3.5">
              <Zap size={13} className="text-arcane-400" /> Core Attributes
            </span>
            {attributes && Object.keys(attributes).length > 0 ? (
              Object.entries(attributes).map(([key, data]) => {
                const value = typeof data === 'object' ? data.value : data;
                const tier = typeof data === 'object' ? data.tier : null;
                return <AttributeBar key={key} name={key} value={value} tier={tier} compact />;
              })
            ) : (
              <p className="text-xs text-slate-400">Complete quests to increase your attributes.</p>
            )}
          </div>

          {/* Achievements Preview */}
          <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
            <span className="eyebrow-amber flex items-center gap-1.5 mb-3.5">
              <Trophy size={13} className="text-arcane-400" /> Recent Achievements
            </span>
            <div className="space-y-2.5">
              {achievements.slice(0, 3).map((a) => (
                <div key={a.id} className="flex items-center gap-3 p-2 rounded-lg bg-ink-850 border border-ink-750">
                  <div className="w-8 h-8 rounded bg-ink-900 border border-ink-700 flex items-center justify-center text-base">
                    {a.icon}
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-slate-200 truncate">{a.title}</p>
                    <p className="text-[10px] text-emerald-400 font-mono">Unlocked</p>
                  </div>
                </div>
              ))}
              {achievements.length === 0 && (
                <p className="text-xs text-slate-400">Complete daily quests to unlock achievements.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/80 backdrop-blur-sm">
          <div className="panel bg-ink-900 w-full max-w-md p-6 border border-ink-700">
            <h2 className="font-display text-lg text-rose-400 mb-2">Delete Directive?</h2>
            <p className="text-sm text-slate-400 mb-4">This quest will be permanently removed from your active log.</p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="flex-1 py-2 rounded-lg border border-ink-700 text-slate-400 hover:bg-ink-800 transition-colors text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="flex-1 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


