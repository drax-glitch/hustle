import React from "react";

const DIFFICULTY_STYLES = {
  EASY: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  MEDIUM: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  HARD: "bg-rose-500/15 text-rose-400 border-rose-500/30",
};

const DIFFICULTY_STARS = { EASY: "★", MEDIUM: "★★", HARD: "★★★" };

const CATEGORY_STYLES = {
  Learning: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  Health: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  Creative: "bg-rose-500/15 text-rose-400 border-rose-500/30",
  Work: "bg-slate-500/15 text-slate-300 border-slate-500/30",
  Wellness: "bg-orange-500/15 text-orange-400 border-orange-500/30",
};

export function CategoryBadge({ category }) {
  const style = CATEGORY_STYLES[category] || "bg-slate-500/15 text-slate-400 border-slate-500/30";
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-md border ${style}`}>{category}</span>
  );
}

export function DifficultyBadge({ difficulty }) {
  const style = DIFFICULTY_STYLES[difficulty] || DIFFICULTY_STYLES.EASY;
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-md border font-medium ${style}`}>
      {DIFFICULTY_STARS[difficulty]} {difficulty}
    </span>
  );
}
