import React, { useEffect, useState, useCallback } from "react";
import { Coins, Sparkles, Check } from "lucide-react";
import * as api from "../api/api";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import LoadingState from "../components/LoadingState.jsx";

const CATEGORIES = ["All", "Avatars", "Frames", "Themes", "Badges", "Companions", "Effects", "Weapons", "Magic"];

export default function Shop() {
  const { user, setUser } = useApp();
  const { addToast } = useToast();
  const [items, setItems] = useState([]);
  const [category, setCategory] = useState("All");
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    try {
      const data = await api.fetchShopItems({ category });
      setItems(data);
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to load shop"), "error");
    } finally {
      setLoading(false);
    }
  }, [category, addToast]);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  const handleBuy = async (item) => {
    setBusyId(item.id);
    try {
      const result = await api.buyItem(item.id);
      setUser({ ...user, gold: result.goldRemaining });
      addToast(`Purchased ${item.name}!`, "success");
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Purchase failed"), "error");
    } finally {
      setBusyId(null);
    }
  };

  const handleEquip = async (item) => {
    setBusyId(item.id);
    try {
      const result = await api.equipItem(item.id);
      if (result.user) setUser(result.user);
      addToast(`Equipped ${item.name}!`, "success");
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Equip failed"), "error");
    } finally {
      setBusyId(null);
    }
  };

  const handleUnequip = async (item) => {
    setBusyId(item.id);
    try {
      const result = await api.unequipItem(item.id);
      if (result.user) setUser(result.user);
      addToast(`Unequipped ${item.name}`, "info");
      await load();
    } catch (err) {
      addToast(api.getErrorMessage(err, "Unequip failed"), "error");
    } finally {
      setBusyId(null);
    }
  };

  if (loading) return <LoadingState label="Browsing the emporium…" />;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <span className="eyebrow-amber">ARSENAL & COSMETICS</span>
          <h1 className="font-display text-3xl font-bold text-white tracking-tight mt-1">The Arcane Emporium</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">Acquire cosmetic gear and identity tokens with earned gold.</p>
        </div>
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-ink-900 border border-ink-700/80 text-arcane-400 font-mono font-bold text-sm">
          <Coins size={15} /> {user.gold.toLocaleString()} Gold
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-1.5 flex-wrap">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors ${
              category === c
                ? "bg-ink-800 text-arcane-400 border border-arcane-500/40 font-semibold"
                : "bg-ink-900 text-slate-400 border border-ink-800 hover:text-slate-200"
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      {/* Items Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {items.map((item) => (
          <div key={item.id} className="panel p-4 bg-ink-900 border border-ink-800 flex flex-col justify-between">
            <div>
              <div className="h-24 rounded-lg bg-ink-850 border border-ink-750 flex items-center justify-center text-4xl relative mb-3">
                {item.icon}
                {item.equipped && (
                  <span className="absolute top-2 right-2 text-[9px] font-mono uppercase font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    Equipped
                  </span>
                )}
              </div>

              <div className="flex items-center justify-between gap-1 mb-1">
                <p className="text-xs font-semibold text-slate-100 truncate">{item.name}</p>
                <span className="text-[9px] font-mono text-slate-400 uppercase">
                  {item.category}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug line-clamp-2">{item.description}</p>
            </div>

            <div className="pt-3 mt-3 border-t border-ink-800/80 flex items-center justify-between gap-2">
              {!item.owned ? (
                <>
                  <span className="text-arcane-400 text-xs font-mono font-bold flex items-center gap-1">
                    <Coins size={12} /> {item.price.toLocaleString()}
                  </span>
                  <button
                    disabled={busyId === item.id || user.gold < item.price}
                    onClick={() => handleBuy(item)}
                    className="text-xs font-bold px-3 py-1.5 rounded-md bg-arcane-500 hover:bg-arcane-400 text-ink-950 disabled:opacity-30 transition-colors shadow-sm"
                  >
                    Acquire
                  </button>
                </>
              ) : item.equippable ? (
                item.equipped ? (
                  <button
                    disabled={busyId === item.id}
                    onClick={() => handleUnequip(item)}
                    className="text-xs font-medium px-3 py-1.5 rounded-md border border-ink-700 text-slate-400 hover:text-slate-200 w-full transition-colors"
                  >
                    Unequip
                  </button>
                ) : (
                  <button
                    disabled={busyId === item.id}
                    onClick={() => handleEquip(item)}
                    className="text-xs font-bold px-3 py-1.5 rounded-md bg-ink-800 hover:bg-ink-750 text-arcane-400 border border-arcane-500/30 w-full transition-colors"
                  >
                    Equip
                  </button>
                )
              ) : (
                <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                  <Check size={12} /> Owned
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

