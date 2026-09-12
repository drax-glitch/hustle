import React from "react";

export default function EmptyState({ message, icon = "📭" }) {
  return (
    <div className="text-center py-10 border border-dashed border-ink-700 rounded-xl">
      <p className="text-2xl mb-2">{icon}</p>
      <p className="text-sm text-slate-400">{message}</p>
    </div>
  );
}
