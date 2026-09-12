import React, { useState } from "react";
import { Check, Flame, Coins, Trash2, Pencil, Swords } from "lucide-react";
import { CategoryBadge, DifficultyBadge } from "./Badge.jsx";

export default function QuestCard({ quest, onComplete, onDelete, onEdit, activeBoss }) {
  const [busy, setBusy] = useState(false);
  const isDone = quest.status === "COMPLETED";

  // Check if quest is linked to active boss
  const isBossLinked = activeBoss && (
    (activeBoss.linkedQuestIds && activeBoss.linkedQuestIds.includes(quest.id)) ||
    (quest.category && activeBoss.category && quest.category.toLowerCase() === activeBoss.category.toLowerCase())
  );

  const bossDamageEstimate = isBossLinked ? Math.round(quest.xpReward * (activeBoss.difficulty === "EPIC" ? 2.5 : activeBoss.difficulty === "HARD" ? 2.0 : 1.5)) : 0;

  const handleToggle = async () => {
    if (isDone || busy) return;
    setBusy(true);
    try {
      await onComplete(quest.id);
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async (e) => {
    e.stopPropagation();
    if (busy || !onDelete) return;
    onDelete(quest.id);
  };

  const handleEdit = (e) => {
    e.stopPropagation();
    if (onEdit) onEdit(quest);
  };

  return (
    <div
      className={`flex items-center justify-between gap-4 p-4 rounded-xl border transition-all ${
        isDone
          ? "bg-ink-800/40 border-ink-700/60 opacity-75"
          : isBossLinked
          ? "bg-gradient-to-r from-ink-800 via-rose-950/20 to-ink-800 border-rose-500/40 hover:border-rose-400/60 shadow-sm shadow-rose-950/20"
          : "bg-ink-800 border-ink-700 hover:border-arcane-600/40"
      }`}
    >
      <div className="flex items-center gap-4 min-w-0 flex-1">
        <button
          onClick={handleToggle}
          disabled={busy || isDone}
          title={isDone ? "Completed" : "Mark as complete"}
          className={`w-6 h-6 shrink-0 rounded-md border flex items-center justify-center transition-colors ${
            isDone
              ? "bg-emerald-500 border-emerald-500 cursor-default"
              : isBossLinked
              ? "border-rose-500 hover:border-rose-400 hover:bg-rose-500/20"
              : "border-ink-600 hover:border-arcane-500"
          }`}
        >
          {isDone && <Check size={14} className="text-white" />}
        </button>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <p className={`text-sm font-medium ${isDone ? "line-through text-slate-500" : "text-slate-100"}`}>
              {quest.title}
            </p>
            {isBossLinked && !isDone && (
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/40 flex items-center gap-1 shadow-sm">
                <Swords size={11} /> BOSS QUEST · 💥 -{bossDamageEstimate} HP
              </span>
            )}
            {quest.dueLabel && !isDone && (
              <span className="text-[11px] text-amber-400 flex items-center gap-1">
                <Flame size={11} /> {quest.dueLabel}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <CategoryBadge category={quest.category} />
            <DifficultyBadge difficulty={quest.difficulty} />
            <span className="text-[11px] text-slate-500">{quest.attribute}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <div className="text-right hidden sm:block">
          <p className="text-sm font-semibold text-arcane-400">+{quest.xpReward} XP</p>
          <p className="text-xs text-amber-400 flex items-center gap-1 justify-end mt-0.5">
            +{quest.goldReward} <Coins size={11} />
          </p>
        </div>
        {onEdit && !isDone && (
          <button onClick={handleEdit} disabled={busy} title="Edit quest"
            className="p-1.5 rounded-lg text-slate-500 hover:text-arcane-400 hover:bg-arcane-500/10">
            <Pencil size={16} />
          </button>
        )}
        {onDelete && (
          <button onClick={handleDelete} disabled={busy} title="Delete quest"
            className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10">
            <Trash2 size={16} />
          </button>
        )}
      </div>
    </div>
  );
}

