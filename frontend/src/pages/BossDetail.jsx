import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Swords, Plus, Calendar, Shield, CheckCircle2, ArrowLeft } from "lucide-react";
import * as api from "../api/api";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import LoadingState from "../components/LoadingState.jsx";
import EmptyState from "../components/EmptyState.jsx";
import BossVictoryModal from "../components/BossVictoryModal.jsx";

const DIFFICULTY_ICONS = {
  EASY: "📊",
  MEDIUM: "⚔️",
  HARD: "🛡️",
  EPIC: "👹",
};

export default function BossDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, setUser } = useApp();
  const { addToast } = useToast();
  const [boss, setBoss] = useState(null);
  const [loading, setLoading] = useState(true);
  const [linkModalOpen, setLinkModalOpen] = useState(false);
  const [availableQuests, setAvailableQuests] = useState([]);
  const [victoryModalOpen, setVictoryModalOpen] = useState(false);
  const [victoryRewards, setVictoryRewards] = useState(null);

  const load = useCallback(async () => {
    try {
      const data = await api.fetchBoss(id);
      setBoss(data);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load boss"), "error");
    } finally {
      setLoading(false);
    }
  }, [id, addToast]);

  const loadAvailableQuests = useCallback(async () => {
    try {
      const allQuests = await api.fetchQuests();
      const linkedQuestIds = boss?.linkedQuests?.map((q) => q.id) || [];
      const available = allQuests.filter((q) => 
        q.status === "ACTIVE" && !linkedQuestIds.includes(q.id)
      );
      setAvailableQuests(available);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load quests"), "error");
    }
  }, [boss, addToast]);

  useEffect(() => {
    load();
  }, [load]);

  const handleOpenLinkModal = () => {
    loadAvailableQuests();
    setLinkModalOpen(true);
  };

  const handleClaimRewards = async () => {
    try {
      const rewards = await api.claimBossRewards(id);
      if (rewards.levelsGained > 0) {
        setUser((prev) => ({ ...prev, level: prev.level + rewards.levelsGained }));
      }
      setVictoryRewards(rewards);
      setVictoryModalOpen(true);
      addToast(`Victory! +${rewards.xpReward} XP, +${rewards.goldReward} Gold, +${rewards.skillPointReward} Skill Point`, "success");
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to claim rewards"), "error");
    }
  };

  const handleLinkQuest = async (questId) => {
    try {
      await api.linkQuestToBoss(id, questId);
      addToast("Quest linked to boss! Completing it will deal damage.", "success");
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to link quest"), "error");
    }
  };

  const handleUnlinkQuest = async (questId) => {
    try {
      await api.unlinkQuestFromBoss(id, questId);
      addToast("Quest unlinked from boss", "success");
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to unlink quest"), "error");
    }
  };

  if (loading) return <LoadingState label="Entering boss arena…" />;
  if (!boss) return <p className="text-slate-500">Boss not found.</p>;

  const hpPercent = boss.hpPercent;
  const isDefeated = boss.status === "defeated";

  return (
    <div className="space-y-8">
      {victoryModalOpen && victoryRewards && (
        <BossVictoryModal
          boss={boss}
          rewards={victoryRewards}
          onClose={() => setVictoryModalOpen(false)}
          onCreateNew={() => {
            setVictoryModalOpen(false);
            navigate("/boss/create");
          }}
        />
      )}

      <div>
        <button
          onClick={() => navigate("/world")}
          className="text-xs font-mono uppercase tracking-wider text-slate-400 hover:text-white transition-colors flex items-center gap-1 mb-2"
        >
          <ArrowLeft size={13} /> Return to World Map
        </button>
      </div>

      {/* Boss Feature Arena */}
      <section className={`panel p-6 sm:p-8 bg-gradient-to-r from-ink-900 ${isDefeated ? "via-emerald-950/20" : "via-rose-950/20"} to-ink-900 border ${isDefeated ? "border-emerald-500/40" : "border-rose-500/40"} relative overflow-hidden`}>
        <div className="flex items-start justify-between gap-6 flex-wrap mb-6">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-ink-850 border-2 border-rose-500/40 flex items-center justify-center text-4xl sm:text-5xl shadow-lg shrink-0">
              👹
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className={isDefeated ? "eyebrow text-emerald-400" : "eyebrow-crimson"}>
                  {isDefeated ? "CAMPAIGN CONQUERED" : "ACTIVE CAMPAIGN TRIAL"}
                </span>
                <span className="text-slate-600">·</span>
                <span className="text-xs font-mono font-semibold text-slate-300">
                  {boss.category} Region
                </span>
              </div>
              <h1 className="font-display text-2xl sm:text-3xl font-bold text-white tracking-tight">{boss.title}</h1>
              <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-xl">{boss.description}</p>
              <div className="flex items-center gap-3 mt-2.5 flex-wrap">
                <span className="text-[11px] font-mono uppercase px-2.5 py-0.5 rounded bg-ink-800 text-slate-200 border border-ink-700">
                  {DIFFICULTY_ICONS[boss.difficulty] || "⚔️"} {boss.difficulty} Trial
                </span>
                {boss.deadline && (
                  <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                    <Calendar size={12} /> Target: {new Date(boss.deadline).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="text-left sm:text-right w-full sm:w-auto pt-4 sm:pt-0 border-t sm:border-t-0 border-ink-800">
            <p className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">
              BOSS INTEGRITY
            </p>
            <p className="text-2xl sm:text-3xl font-mono font-bold text-white">
              {boss.currentHp.toLocaleString()} <span className="text-sm text-slate-500 font-normal">/ {boss.maxHp.toLocaleString()} HP</span>
            </p>
          </div>
        </div>

        {/* HP Bar */}
        <div className="space-y-2">
          <div className="progress-track h-3 bg-ink-950 border border-ink-800">
            <div
              className={`progress-fill bg-gradient-to-r ${isDefeated ? "from-emerald-500 to-emerald-400" : "from-rose-500 to-rose-400"}`}
              style={{ width: `${hpPercent}%` }}
            />
          </div>
          <div className="flex justify-between text-xs font-mono text-slate-400">
            <span>Phase {boss.currentPhase} — {boss.phaseName}</span>
            <span>{hpPercent}% HP Remaining</span>
          </div>
        </div>

        {/* Rewards */}
        {isDefeated && (
          <div className="mt-6 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <Shield size={18} className="text-emerald-400" />
              <div>
                <span className="text-emerald-300 font-bold text-sm">Boss Defeated!</span>
                <p className="text-xs text-slate-400 font-mono">+1,000 XP · +500 Gold · +1 Skill Point</p>
              </div>
            </div>
            {boss.rewardClaimed ? (
              <span className="text-xs px-3 py-1.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-semibold border border-emerald-500/40 flex items-center gap-1.5">
                <CheckCircle2 size={13} /> Rewards Claimed
              </span>
            ) : (
              <button
                onClick={handleClaimRewards}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs px-4 py-2 rounded-lg transition-colors shadow-sm"
              >
                Claim Victory Rewards
              </button>
            )}
          </div>
        )}
      </section>

      {/* Linked Quests */}
      <section className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-ink-800">
          <div>
            <span className="eyebrow-amber flex items-center gap-1.5">
              <Swords size={13} className="text-arcane-400" /> Linked Quests
            </span>
            <p className="text-xs text-slate-400 mt-0.5">Directives linked to strike this boss and advance phases.</p>
          </div>
          {boss.status === "active" && (
            <button
              onClick={handleOpenLinkModal}
              className="text-xs bg-arcane-500 hover:bg-arcane-400 text-ink-950 font-bold px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1 shadow-sm"
            >
              <Plus size={13} /> Link Quest
            </button>
          )}
        </div>

        {boss.linkedQuests && boss.linkedQuests.length > 0 ? (
          <div className="space-y-2">
            {boss.linkedQuests.map((quest) => (
              <div key={quest.id} className="p-3 rounded-lg bg-ink-850 border border-ink-750 flex items-center justify-between gap-4">
                <div>
                  <p className="text-slate-200 font-medium text-sm">{quest.title}</p>
                  <p className="text-[11px] text-slate-400 font-mono capitalize">{quest.category} • {quest.difficulty}</p>
                </div>
                <button
                  onClick={() => handleUnlinkQuest(quest.id)}
                  className="text-xs font-mono text-rose-400 hover:text-rose-300 px-2 py-1 transition-colors"
                >
                  Unlink
                </button>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<Swords size={28} />}
            message="No quests linked to this boss yet."
            action="Link directives above to deal damage upon completion."
          />
        )}
      </section>

      {/* Link Quest Modal */}
      {linkModalOpen && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center px-4 bg-black/80 backdrop-blur-sm">
          <div className="panel bg-ink-900 w-full max-w-md p-6 border border-ink-700">
            <h2 className="font-display text-lg font-bold text-white mb-3">Link Active Directive</h2>
            <div className="space-y-2 max-h-64 overflow-y-auto mb-4">
              {availableQuests.map((quest) => (
                <button
                  key={quest.id}
                  onClick={() => {
                    handleLinkQuest(quest.id);
                    setLinkModalOpen(false);
                  }}
                  className="w-full p-3 rounded-lg bg-ink-850 border border-ink-750 hover:border-arcane-500/60 text-left transition-colors"
                >
                  <p className="text-slate-200 font-medium text-xs truncate">{quest.title}</p>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">{quest.category} • {quest.difficulty} • +{quest.xpReward} XP</p>
                </button>
              ))}
              {availableQuests.length === 0 && (
                <p className="text-xs text-slate-400 text-center py-4">No available unlinked quests.</p>
              )}
            </div>
            <button
              onClick={() => setLinkModalOpen(false)}
              className="w-full bg-ink-800 hover:bg-ink-750 text-slate-300 text-xs font-semibold py-2 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

