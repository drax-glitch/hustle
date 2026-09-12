import React, { useEffect, useState } from "react";
import { Zap, CheckSquare, Flame, Coins, Crown } from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";
import * as api from "../api/api";
import { useToast } from "../context/ToastContext.jsx";
import LoadingState from "../components/LoadingState.jsx";

export default function ProgressPage() {
  const { addToast } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.fetchProgress()
      .then(setData)
      .catch((err) => addToast(api.getErrorMessage(err, "Failed to load progress"), "error"))
      .finally(() => setLoading(false));
  }, [addToast]);

  if (loading) return <LoadingState label="Loading progress report…" />;
  if (!data) return <p className="text-slate-500">Could not load progress.</p>;

  const summary = [
    { icon: <Zap size={16} className="text-arcane-400" />, value: (data.todayXp ?? 0).toLocaleString(), label: "Today's XP" },
    { icon: <CheckSquare size={16} className="text-emerald-400" />, value: data.todayQuests ?? 0, label: "Quests Today" },
    { icon: <Flame size={16} className="text-orange-400" />, value: `${data.currentStreak}d`, label: "Current Streak" },
    { icon: <Flame size={16} className="text-amber-400" />, value: `${data.bestStreak}d`, label: "Best Streak" },
    { icon: <Coins size={16} className="text-amber-400" />, value: (data.todayGold ?? 0).toLocaleString(), label: "Today's Gold" },
    { icon: <Zap size={16} className="text-amber-400" />, value: data.totalXp.toLocaleString(), label: "Lifetime XP" },
    { icon: <CheckSquare size={16} className="text-emerald-400" />, value: data.questsDone, label: "Lifetime Quests" },
  ];

  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl text-white flex items-center gap-2">Analytics & Progress</h1>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {summary.map((s) => (
          <div key={s.label} className="panel p-4 flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-ink-800 border border-ink-700 flex items-center justify-center">
              {s.icon}
            </div>
            <div>
              <p className="text-lg font-semibold text-white">{s.value}</p>
              <p className="text-[11px] text-slate-500">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="panel p-6">
          <h2 className="font-display text-sm text-white mb-4 flex items-center gap-2">
            <Zap size={15} className="text-arcane-400" /> Weekly XP
          </h2>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={data.weeklyXp}>
              <CartesianGrid strokeDasharray="3 3" stroke="#20203f" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ background: "#13132a", border: "1px solid #20203f" }} />
              <Line type="monotone" dataKey="xp" stroke="#8b5cf6" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="panel p-6">
          <h2 className="font-display text-sm text-white mb-4 flex items-center gap-2">
            <CheckSquare size={15} className="text-cyan-400" /> Daily Quests
          </h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.dailyQuests}>
              <CartesianGrid strokeDasharray="3 3" stroke="#20203f" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ background: "#13132a", border: "1px solid #20203f" }} />
              <Bar dataKey="quests" fill="#22d3ee" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="panel p-6">
        <h2 className="font-display text-sm text-white mb-4 flex items-center gap-2">
          <Crown size={15} className="text-amber-400" /> Level Journey
        </h2>
        <div className="flex gap-2 flex-wrap">
          {data.levelJourney.map((lvl) => (
            <div key={lvl.level}
              className={`w-10 h-10 rounded-lg flex items-center justify-center text-xs font-semibold ${
                lvl.current
                  ? "bg-arcane-500 text-white shadow-glow"
                  : lvl.completed
                  ? "bg-arcane-600/30 text-arcane-300"
                  : "bg-ink-800 text-slate-600 border border-ink-700"
              }`}>
              {lvl.completed || lvl.current ? "✓" : lvl.level}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
