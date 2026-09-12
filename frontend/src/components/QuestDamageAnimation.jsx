import React from "react";
import { Skull, Zap } from "lucide-react";

export default function QuestDamageAnimation({ damage, isCritical, onClose }) {
  React.useEffect(() => {
    const timer = setTimeout(onClose, 2000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center pointer-events-none">
      <div className="animate-bounce-in text-center">
        <div className={`flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r ${
          isCritical ? "from-rose-600 to-rose-500" : "from-orange-600 to-orange-500"
        } text-white font-bold text-2xl shadow-glow`}>
          {isCritical ? <Zap size={24} /> : <Skull size={24} />}
          <span>{isCritical ? "CRITICAL HIT!" : "HIT!"}</span>
        </div>
        <div className="mt-2 text-3xl font-display text-rose-400 font-bold">
          -{damage} HP
        </div>
      </div>
    </div>
  );
}
