import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle } from "lucide-react";
import * as api from "../api/api";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";

const GOAL_OPTIONS = [
  { id: "Health", label: "Health & Fitness", icon: "❤️", description: "Physical wellbeing" },
  { id: "Knowledge", label: "Knowledge & Learning", icon: "🧠", description: "Intellectual growth" },
  { id: "Career", label: "Career & Productivity", icon: "💼", description: "Professional development" },
  { id: "Discipline", label: "Discipline & Habits", icon: "🔥", description: "Building consistency" },
  { id: "Creativity", label: "Creativity & Expression", icon: "🎨", description: "Artistic pursuits" },
];

function HustleMark({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="6" width="5" height="20" rx="1.5" fill="#f59e0b" />
      <rect x="23" y="4" width="5" height="22" rx="1.5" fill="#f59e0b" />
      <path d="M9 18 L23 12" stroke="#f59e0b" strokeWidth="4.5" strokeLinecap="round" />
    </svg>
  );
}

export default function Onboarding() {
  const navigate = useNavigate();
  const { setUser } = useApp();
  const { addToast } = useToast();
  const [step, setStep] = useState(1);
  const [selectedGoals, setSelectedGoals] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleGoalToggle = (goalId) => {
    setSelectedGoals((prev) =>
      prev.includes(goalId) ? prev.filter((id) => id !== goalId) : [...prev, goalId]
    );
  };

  const handleContinue = async () => {
    if (step === 1) {
      setStep(2);
    } else if (step === 2) {
      if (selectedGoals.length === 0) {
        addToast("Please select at least one goal", "error");
        return;
      }
      setStep(3);
    } else {
      setIsSubmitting(true);
      try {
        const result = await api.completeOnboarding(selectedGoals);
        if (result.user) setUser(result.user);
        addToast("Welcome to HUSTLE! Your adventure begins.", "success");
        navigate("/");
      } catch (err) {
        addToast(api.getErrorMessage(err, "Failed to complete setup"), "error");
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-ink-950 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <HustleMark size={28} />
            <span className="font-display font-bold text-xl tracking-tight text-white">HUSTLE</span>
          </div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-amber-500/70 font-bold">Character Setup</p>
        </div>

        <div className="panel bg-ink-900 border border-ink-800 p-8">
          {step === 1 && (
            <div className="text-center">
              <h2 className="font-display text-2xl text-white mb-3 tracking-tight">Welcome, Adventurer</h2>
              <p className="text-slate-400 mb-8 leading-relaxed">
                Your real-life journey is about to become your greatest adventure.
                Turn daily tasks into quests, progress into levels, and habits into superpowers.
              </p>
              <button
                onClick={handleContinue}
                className="w-full bg-amber-500 hover:bg-amber-400 text-ink-950 font-bold py-3 rounded-lg transition-colors tracking-wide"
              >
                BEGIN JOURNEY
              </button>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="font-display text-xl text-white mb-1 tracking-tight">Choose Your Focus</h2>
              <p className="text-slate-500 text-sm mb-6">Select the areas you want to level up (choose 1 or more)</p>
              <div className="space-y-2.5 mb-8">
                {GOAL_OPTIONS.map((goal) => (
                  <button
                    key={goal.id}
                    onClick={() => handleGoalToggle(goal.id)}
                    className={`w-full p-4 rounded-xl border flex items-center gap-4 transition-all text-left ${
                      selectedGoals.includes(goal.id)
                        ? "bg-amber-500/10 border-amber-500/40"
                        : "bg-ink-850 border-ink-750 hover:border-ink-700"
                    }`}
                  >
                    <span className="text-2xl">{goal.icon}</span>
                    <div className="flex-1">
                      <p className="text-slate-200 font-medium text-sm">{goal.label}</p>
                      <p className="text-slate-500 text-xs mt-0.5">{goal.description}</p>
                    </div>
                    {selectedGoals.includes(goal.id) && (
                      <CheckCircle size={18} className="text-amber-400 shrink-0" />
                    )}
                  </button>
                ))}
              </div>
              <button
                onClick={handleContinue}
                disabled={selectedGoals.length === 0}
                className="w-full bg-amber-500 hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed text-ink-950 font-bold py-3 rounded-lg transition-colors tracking-wide"
              >
                CONTINUE
              </button>
            </div>
          )}

          {step === 3 && (
            <div className="text-center">
              <h2 className="font-display text-xl text-white mb-3 tracking-tight">Starter Quests Ready</h2>
              <p className="text-slate-400 mb-6 leading-relaxed">
                Based on your goals, starter quests have been prepared for your adventure.
              </p>
              <div className="space-y-2 mb-8 text-left">
                {selectedGoals.map((goal) => (
                  <div key={goal} className="p-3 rounded-lg bg-ink-850 border border-ink-750 flex items-center gap-3">
                    <span className="text-lg">{GOAL_OPTIONS.find((g) => g.id === goal)?.icon}</span>
                    <div>
                      <p className="text-slate-200 text-sm font-medium">{GOAL_OPTIONS.find((g) => g.id === goal)?.label}</p>
                      <p className="text-slate-500 text-xs">2 starter quests created</p>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={handleContinue}
                disabled={isSubmitting}
                className="w-full bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-ink-950 font-bold py-3 rounded-lg transition-colors tracking-wide"
              >
                {isSubmitting ? "Setting up…" : "START YOUR ADVENTURE"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
