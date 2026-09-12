import React from "react";
import DailyChronicle from "../components/DailyChronicle.jsx";

export default function Chronicle() {
  return (
    <div className="space-y-8">
      <div>
        <span className="eyebrow-amber">JOURNAL OF ADVENTURES</span>
        <h1 className="font-display text-3xl font-bold text-white tracking-tight mt-1">Daily Chronicle</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">Your chronicled milestones, boss engagements, and realm growth over time.</p>
      </div>
      <DailyChronicle isPreview={false} maxItems={30} />
    </div>
  );
}

