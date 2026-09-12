import React, { useEffect, useState, useCallback } from "react";
import { Plus, X, Pencil } from "lucide-react";
import * as api from "../api/api";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import { useQuestCompletion } from "../hooks/useQuestCompletion.js";
import QuestCard from "../components/QuestCard.jsx";
import LoadingState from "../components/LoadingState.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LevelUpModal from "../components/LevelUpModal.jsx";

const STATUS_TABS = ["All", "Active", "Completed"];
const CATEGORY_TABS = ["All", "Learning", "Health", "Creative", "Wellness", "Work"];
const DIFFICULTIES = ["EASY", "MEDIUM", "HARD"];
const ATTRIBUTES = ["Strength", "Intelligence", "Discipline", "Creativity", "Vitality"];

const EMPTY_FORM = {
  title: "", category: "Learning", difficulty: "EASY", attribute: "Intelligence", dueLabel: "Today",
};

export default function Quests() {
  const { setUser } = useApp();
  const { addToast } = useToast();
  const [quests, setQuests] = useState([]);
  const [statusTab, setStatusTab] = useState("All");
  const [categoryTab, setCategoryTab] = useState("All");
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingQuest, setEditingQuest] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  const load = useCallback(async () => {
    try {
      const status = statusTab === "All" ? undefined : statusTab.toUpperCase();
      const data = await api.fetchQuests({ status, category: categoryTab });
      setQuests(data);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load quests"), "error");
    } finally {
      setLoading(false);
    }
  }, [statusTab, categoryTab, addToast]);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  const { handleComplete, levelUp, dismissLevelUp } = useQuestCompletion(load);

  const openCreate = () => {
    setEditingQuest(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
  };

  const openEdit = (quest) => {
    setEditingQuest(quest);
    setForm({
      title: quest.title,
      category: quest.category,
      difficulty: quest.difficulty,
      attribute: quest.attribute,
      dueLabel: quest.dueLabel,
    });
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    try {
      if (editingQuest) {
        await api.updateQuest(editingQuest.id, form);
        addToast("Directive updated!", "success");
      } else {
        await api.createQuest(form);
        addToast("Directive inscribed!", "success");
      }
      setShowForm(false);
      setEditingQuest(null);
      setForm(EMPTY_FORM);
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to save quest"), "error");
    }
  };

  const handleDelete = async (id) => {
    setDeleteConfirmId(id);
  };

  const confirmDelete = async () => {
    if (!deleteConfirmId) return;
    try {
      await api.deleteQuest(deleteConfirmId);
      addToast("Quest deleted", "info");
      setDeleteConfirmId(null);
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to delete quest"), "error");
    }
  };

  const activeCount = quests.filter((q) => q.status === "ACTIVE").length;

  if (loading) return <LoadingState label="Consulting quest log…" />;

  return (
    <div className="space-y-8">
      {levelUp && (
        <LevelUpModal
          level={levelUp.level}
          skillPoints={levelUp.skillPoints}
          goldBonus={levelUp.goldBonus}
          onClose={dismissLevelUp}
        />
      )}

      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <span className="eyebrow-amber">DIRECTIVES ARCHIVE</span>
          <h1 className="font-display text-3xl font-bold text-white tracking-tight mt-1">Active Quests & Directives</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">{activeCount} active directives in field queue</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-1.5 bg-arcane-500 hover:bg-arcane-400 text-ink-950 font-bold text-xs px-4 py-2 rounded-lg transition-colors shadow-sm"
        >
          <Plus size={14} /> Inscribe Directive
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="flex items-center gap-1 bg-ink-900 p-1 rounded-lg border border-ink-800">
          {STATUS_TABS.map((t) => (
            <button
              key={t}
              onClick={() => setStatusTab(t)}
              className={`text-xs px-3 py-1 rounded font-medium transition-colors ${
                statusTab === t
                  ? "bg-ink-800 text-arcane-400 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <span className="w-px h-5 bg-ink-800 mx-1 hidden sm:block" />

        <div className="flex items-center gap-1 flex-wrap">
          {CATEGORY_TABS.map((c) => (
            <button
              key={c}
              onClick={() => setCategoryTab(c)}
              className={`text-xs px-2.5 py-1 rounded-md transition-colors ${
                categoryTab === c
                  ? "bg-ink-800 text-slate-100 border border-ink-700 font-medium"
                  : "bg-ink-900 text-slate-400 border border-ink-850 hover:text-slate-200"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Quests Container */}
      <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800 space-y-2.5">
        {quests.map((q) => (
          <QuestCard
            key={q.id}
            quest={q}
            onComplete={handleComplete}
            onDelete={handleDelete}
            onEdit={q.status === "ACTIVE" ? () => openEdit(q) : undefined}
          />
        ))}
        {quests.length === 0 && (
          <EmptyState message="No directives match this filter." icon="📜" />
        )}
      </div>

      {/* Inscribe / Edit Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4 backdrop-blur-sm">
          <div className="panel bg-ink-900 w-full max-w-md p-6 border border-ink-700">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-ink-800">
              <h2 className="font-display text-lg font-bold text-white flex items-center gap-2">
                {editingQuest ? <><Pencil size={15} /> Edit Directive</> : "Inscribe Directive"}
              </h2>
              <button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-200">
                <X size={16} />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-3.5">
              <input
                autoFocus
                placeholder="Quest directive title..."
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="w-full bg-ink-850 border border-ink-750 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-arcane-500"
              />
              <div className="grid grid-cols-2 gap-3">
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  className="bg-ink-850 border border-ink-750 rounded-lg px-3 py-2 text-xs text-slate-200"
                >
                  {CATEGORY_TABS.filter((c) => c !== "All").map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
                <select
                  value={form.difficulty}
                  onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
                  className="bg-ink-850 border border-ink-750 rounded-lg px-3 py-2 text-xs text-slate-200"
                >
                  {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <select
                  value={form.attribute}
                  onChange={(e) => setForm({ ...form, attribute: e.target.value })}
                  className="bg-ink-850 border border-ink-750 rounded-lg px-3 py-2 text-xs text-slate-200"
                >
                  {ATTRIBUTES.map((a) => <option key={a} value={a}>{a}</option>)}
                </select>
                <select
                  value={form.dueLabel}
                  onChange={(e) => setForm({ ...form, dueLabel: e.target.value })}
                  className="bg-ink-850 border border-ink-750 rounded-lg px-3 py-2 text-xs text-slate-200"
                >
                  {["Today", "Tomorrow", "This Week"].map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
              <button
                type="submit"
                className="w-full bg-arcane-500 hover:bg-arcane-400 text-ink-950 text-xs font-bold py-2.5 rounded-lg transition-colors shadow-sm"
              >
                {editingQuest ? "Save Changes" : "Inscribe Directive"}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/80 backdrop-blur-sm">
          <div className="panel bg-ink-900 w-full max-w-md p-6 border border-ink-700">
            <h2 className="font-display text-lg text-rose-400 mb-2">Delete Directive?</h2>
            <p className="text-sm text-slate-400 mb-4">This quest will be permanently removed from your log.</p>
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

