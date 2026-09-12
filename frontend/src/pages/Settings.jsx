import React, { useState } from "react";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import * as api from "../api/api";

export default function Settings() {
  const { user, setUser, logout } = useApp();
  const { addToast } = useToast();
  const [form, setForm] = useState({
    displayName: user.displayName,
    title: user.title,
    dailyGoal: user.dailyGoal,
  });
  const [notifs, setNotifs] = useState(user.settings);
  const [saving, setSaving] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [showResetStreakConfirm, setShowResetStreakConfirm] = useState(false);

  const saveProfile = async () => {
    setSaving(true);
    try {
      const updated = await api.updateSettings(form);
      setUser(updated);
      addToast("Profile saved!", "success");
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to save profile"), "error");
    } finally {
      setSaving(false);
    }
  };

  const toggleNotif = async (key) => {
    const next = { ...notifs, [key]: !notifs[key] };
    setNotifs(next);
    try {
      await api.updateSettings({ [key]: next[key] });
    } catch (err) {
      setNotifs(notifs);
      addToast(api.getErrorMessage(err, "Failed to update setting"), "error");
    }
  };

  const handleResetStreak = async () => {
    setShowResetStreakConfirm(true);
  };

  const confirmResetStreak = async () => {
    try {
      const res = await api.resetStreak();
      setUser({ ...user, streak: res.streak, bestStreak: res.bestStreak });
      setShowResetStreakConfirm(false);
      addToast("Streak reset", "info");
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to reset streak"), "error");
    }
  };

  const handleResetCharacter = async () => {
    try {
      const updated = await api.resetCharacter();
      setUser(updated);
      setShowResetConfirm(false);
      addToast("Character reset complete", "info");
    } catch (err) {
      addToast(api.getErrorMessage(err, "Reset failed"), "error");
    }
  };

  const NOTIF_LABELS = {
    questReminders: { label: "Quest Reminders", hint: "In-app reminders (push notifications coming soon)" },
    streakAlerts: { label: "Streak Alerts", hint: "In-app streak warnings" },
    levelUpCelebrations: { label: "Level Up Celebrations", hint: "Show level-up modal on level increase" },
    achievementUnlocks: { label: "Achievement Unlocks", hint: "Show toast when achievements unlock" },
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="font-display text-2xl text-white">Settings</h1>

      <div className="panel p-6">
        <h2 className="text-xs uppercase tracking-wide text-slate-500 mb-4">Profile</h2>
        <div className="space-y-3">
          <Field label="Display Name" value={form.displayName}
            onChange={(v) => setForm({ ...form, displayName: v })} />
          <Field label="Character Title" value={form.title}
            onChange={(v) => setForm({ ...form, title: v })} />
          <Field label="Daily Goal" type="number" value={form.dailyGoal}
            onChange={(v) => setForm({ ...form, dailyGoal: Number(v) })} suffix="quests/day" />
        </div>
        <button onClick={saveProfile} disabled={saving}
          className="mt-4 bg-arcane-600 hover:bg-arcane-500 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50">
          {saving ? "Saving…" : "Save profile"}
        </button>
      </div>

      <div className="panel p-6">
        <h2 className="text-xs uppercase tracking-wide text-slate-500 mb-1">In-App Notifications</h2>
        <p className="text-xs text-slate-600 mb-4">These control in-app toasts and modals. Push notifications are not yet available.</p>
        <div className="space-y-4">
          {Object.entries(NOTIF_LABELS).map(([key, { label, hint }]) => (
            <div key={key} className="flex items-center justify-between gap-4">
              <div>
                <span className="text-sm text-slate-300">{label}</span>
                <p className="text-[11px] text-slate-600">{hint}</p>
              </div>
              <button onClick={() => toggleNotif(key)}
                className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${
                  notifs[key] ? "bg-arcane-600" : "bg-ink-700"
                }`}>
                <span className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                  notifs[key] ? "translate-x-5" : "translate-x-0.5"
                }`} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="panel p-6 border-rose-900/40">
        <h2 className="text-xs uppercase tracking-wide text-rose-400 mb-4">Danger Zone</h2>
        <div className="flex gap-3 flex-wrap">
          <button onClick={handleResetStreak}
            className="text-sm px-4 py-2 rounded-lg border border-orange-600/40 text-orange-400 hover:bg-orange-600/10">
            Reset Streak
          </button>
          <button onClick={() => setShowResetConfirm(true)}
            className="text-sm px-4 py-2 rounded-lg border border-rose-600/40 text-rose-400 hover:bg-rose-600/10">
            Reset Character
          </button>
          <button onClick={logout}
            className="text-sm px-4 py-2 rounded-lg border border-ink-600 text-slate-400 hover:bg-ink-800">
            Log out
          </button>
        </div>
      </div>

      {showResetConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/70">
          <div className="panel bg-ink-900 w-full max-w-md p-6">
            <h2 className="font-display text-lg text-rose-400 mb-3">Reset Character?</h2>
            <p className="text-sm text-slate-400 mb-4">This will permanently reset:</p>
            <ul className="text-sm text-slate-500 space-y-1 mb-4 list-disc list-inside">
              <li>XP, Level, Gold, Skill Points</li>
              <li>Attributes & Streaks</li>
              <li>All Quests</li>
              <li>Achievements</li>
              <li>XP History</li>
              <li>Inventory & Equipment</li>
            </ul>
            <p className="text-xs text-rose-400 mb-5">This cannot be undone. Your account will remain.</p>
            <div className="flex gap-3">
              <button onClick={() => setShowResetConfirm(false)}
                className="flex-1 py-2.5 rounded-lg border border-ink-600 text-slate-400 hover:bg-ink-800">
                Cancel
              </button>
              <button onClick={handleResetCharacter}
                className="flex-1 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium">
                Reset
              </button>
            </div>
          </div>
        </div>
      )}

      {showResetStreakConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/70">
          <div className="panel bg-ink-900 w-full max-w-md p-6">
            <h2 className="font-display text-lg text-orange-400 mb-3">Reset Streak?</h2>
            <p className="text-sm text-slate-400 mb-4">This will reset your current streak to 0. Your best streak will be preserved.</p>
            <p className="text-xs text-orange-400 mb-5">This cannot be undone.</p>
            <div className="flex gap-3">
              <button onClick={() => setShowResetStreakConfirm(false)}
                className="flex-1 py-2.5 rounded-lg border border-ink-600 text-slate-400 hover:bg-ink-800">
                Cancel
              </button>
              <button onClick={confirmResetStreak}
                className="flex-1 py-2.5 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-medium">
                Reset Streak
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, value, onChange, type = "text", suffix }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <label className="text-sm text-slate-400 shrink-0">{label}</label>
      <div className="flex items-center gap-2 bg-ink-800 border border-ink-700 rounded-lg px-3 py-1.5">
        <input type={type} value={value} onChange={(e) => onChange(e.target.value)}
          className="bg-transparent text-sm text-right text-slate-100 focus:outline-none w-40" />
        {suffix && <span className="text-xs text-slate-500">{suffix}</span>}
      </div>
    </div>
  );
}
