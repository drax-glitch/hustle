import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { RefreshCw, ArrowRight, Sparkles, MapPin, Compass } from "lucide-react";
import * as api from "../api/api";
import { useToast } from "../context/ToastContext.jsx";

export default function GameMaster() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(false);

  const loadAdvice = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    else setLoading(true);
    setError(false);
    try {
      const response = await api.fetchGameMasterAdvice(isManual);
      setData(response);
    } catch (err) {
      setError(true);
      addToast(api.getErrorMessage(err, "Failed to get Game Master advice"), "error");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAdvice(false);
  }, []);

  const handleActionClick = () => {
    if (!data) return;
    if (data.action_path) {
      navigate(data.action_path);
    } else if (data.quest_id) {
      navigate("/quests");
    } else if (data.boss_id) {
      navigate(`/boss/${data.boss_id}`);
    } else if (data.region) {
      navigate("/world");
    } else if (data.recommended_action && data.recommended_action.toLowerCase().includes("skill")) {
      navigate("/skills");
    } else {
      navigate("/quests");
    }
  };

  if (loading) {
    return (
      <div className="panel p-5 bg-ink-900/60 border border-ink-800">
        <div className="flex items-center gap-3 text-slate-400">
          <RefreshCw size={16} className="animate-spin text-arcane-400" />
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">Consulting your advisor…</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="panel p-5 bg-ink-900/60 border border-ink-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 text-slate-400">
            <Compass size={18} className="text-arcane-400" />
            <div>
              <p className="text-sm font-semibold text-slate-200">Your advisor is standing by.</p>
              <p className="text-xs text-slate-400">Complete any active quest to get your next move.</p>
            </div>
          </div>
          <button
            onClick={() => loadAdvice(true)}
            className="text-xs px-3 py-1.5 rounded-lg bg-ink-800 hover:bg-ink-700 text-slate-300 border border-ink-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const advice = data.advice || data;
  const briefing = data.briefing || {};

  const priorityStyles = {
    high: "bg-rose-500/10 border-rose-500/30 text-rose-400",
    medium: "bg-arcane-500/10 border-arcane-500/30 text-arcane-400",
    low: "bg-slate-500/10 border-slate-500/30 text-slate-400",
  };

  const priorityBadge = priorityStyles[advice.priority] || priorityStyles.medium;

  return (
    <div className="panel p-5 sm:p-6 bg-ink-900 border border-ink-800/90 relative overflow-hidden">
      {/* Header bar */}
      <div className="flex items-center justify-between gap-4 mb-3.5">
        <div className="flex items-center gap-2.5">
          <span className="eyebrow-amber flex items-center gap-1.5">
            <Compass size={13} className="text-arcane-400" /> Your Next Move
          </span>
          <span className="text-slate-600">·</span>
          <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${priorityBadge}`}>
            {advice.priority} priority
          </span>
        </div>
        <button
          onClick={() => loadAdvice(true)}
          disabled={refreshing}
          className="text-slate-400 hover:text-white p-1.5 rounded-md hover:bg-ink-800 border border-transparent hover:border-ink-700 transition-colors disabled:opacity-50"
          title="Refresh advisor"
        >
          <RefreshCw size={13} className={refreshing ? "animate-spin text-arcane-400" : ""} />
        </button>
      </div>

      {/* Advisory message */}
      <div className="border-l-2 border-arcane-500/60 pl-4 py-1 mb-4">
        <p className="text-slate-200 text-sm md:text-base font-light leading-relaxed italic">
          "{advice.message}"
        </p>
        <p className="text-[11px] text-slate-400 font-mono mt-1.5">
          — {briefing.greeting || "HUSTLE Advisor"}
        </p>
      </div>

      {/* Directive Action Banner */}
      {advice.recommended_action && (
        <div className="p-3 sm:p-4 rounded-lg bg-ink-850 border border-ink-750 flex items-center justify-between gap-4 flex-wrap">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-arcane-400 flex items-center gap-1">
                <Sparkles size={11} /> Suggested Action
              </span>
              {advice.region && (
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-ink-800 text-slate-400 border border-ink-700 flex items-center gap-1">
                  <MapPin size={9} /> {advice.region}
                </span>
              )}
            </div>
            <p className="text-white font-semibold text-sm truncate">{advice.recommended_action}</p>
            {advice.reason && (
              <p className="text-xs text-slate-400 mt-0.5">{advice.reason}</p>
            )}
          </div>

          <button
            onClick={handleActionClick}
            className="bg-arcane-500 hover:bg-arcane-400 text-ink-950 font-bold text-xs px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5 shrink-0 shadow-sm"
          >
            <span>{advice.action_label || "Execute Directive"}</span>
            <ArrowRight size={13} />
          </button>
        </div>
      )}
    </div>
  );
}

