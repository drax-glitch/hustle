import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Swords, Calendar, MapPin } from "lucide-react";
import * as api from "../api/api";
import { useToast } from "../context/ToastContext.jsx";

const CATEGORIES = ["Health", "Learning", "Work", "Creative", "Wellness"];
const DIFFICULTIES = ["EASY", "MEDIUM", "HARD", "EPIC"];

export default function BossCreate() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("Work");
  const [difficulty, setDifficulty] = useState("MEDIUM");
  const [deadline, setDeadline] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      addToast("Please fill in all required fields", "error");
      return;
    }

    setIsSubmitting(true);
    try {
      const bossData = {
        title: title.trim(),
        description: description.trim(),
        category,
        difficulty,
        deadline: deadline || null,
      };
      const boss = await api.createBoss(bossData);
      addToast(`Boss battle started: ${boss.title}!`, "success");
      navigate(`/boss/${boss.id}`);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to create boss"), "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-2">
        <button onClick={() => navigate("/world")} className="text-slate-400 hover:text-white">
          ← Back to World
        </button>
      </div>

      <div className="panel p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-rose-500 to-rose-400 flex items-center justify-center text-4xl mx-auto mb-4 shadow-glow">
            👹
          </div>
          <h1 className="font-display text-2xl text-white">Begin a New Battle</h1>
          <p className="text-slate-500 mt-2">Turn your major goal into an epic boss battle</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm text-slate-400 mb-2">What challenge are you facing?</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Build my portfolio"
              className="w-full bg-ink-800 border border-ink-700 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-arcane-500"
              maxLength={150}
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">Describe your mission</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Create a professional portfolio website before internship applications."
              className="w-full bg-ink-800 border border-ink-700 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-arcane-500 resize-none"
              rows={3}
              maxLength={500}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">Region</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-ink-800 border border-ink-700 rounded-xl px-4 py-3 text-slate-100 focus:outline-none focus:border-arcane-500"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-2">Difficulty</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full bg-ink-800 border border-ink-700 rounded-xl px-4 py-3 text-slate-100 focus:outline-none focus:border-arcane-500"
              >
                {DIFFICULTIES.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">Deadline (optional)</label>
            <input
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              className="w-full bg-ink-800 border border-ink-700 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-arcane-500"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 text-white font-semibold py-3 rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Swords size={18} />
            {isSubmitting ? "Creating..." : "START BATTLE"}
          </button>
        </form>
      </div>
    </div>
  );
}
