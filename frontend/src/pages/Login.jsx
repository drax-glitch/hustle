import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../context/AppContext.jsx";
import { getErrorMessage } from "../api/api";

function HustleMark({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="6" width="5" height="20" rx="1.5" fill="#f59e0b" />
      <rect x="23" y="4" width="5" height="22" rx="1.5" fill="#f59e0b" />
      <path d="M9 18 L23 12" stroke="#f59e0b" strokeWidth="4.5" strokeLinecap="round" />
    </svg>
  );
}

export default function Login() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "", displayName: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { loginUser, registerUser } = useApp();
  const navigate = useNavigate();

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") {
        await loginUser({ username: form.username, password: form.password });
      } else {
        if (form.password.length < 8) {
          setError("Password must be at least 8 characters");
          setBusy(false);
          return;
        }
        await registerUser(form);
      }
      navigate("/");
    } catch (err) {
      const msg = getErrorMessage(err, "Unable to connect to HUSTLE servers.");
      setError(typeof msg === "string" ? msg : "Unable to connect to HUSTLE servers.");
      console.error("[HUSTLE auth error]", err?.response?.status, msg);
    } finally {
      setBusy(false);
    }
  };

  const isRegister = mode === "register";

  return (
    <div className="min-h-screen flex" style={{ background: "#090a0f" }}>
      {/* LEFT brand panel — desktop only */}
      <div className="hidden lg:flex lg:w-[52%] flex-col justify-between p-14 border-r border-white/5 relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none" style={{
          backgroundImage: "radial-gradient(circle at 80% 20%, rgba(245,158,11,0.04) 0%, transparent 60%)",
        }} />
        <div className="flex items-center gap-3 relative z-10">
          <HustleMark size={28} />
          <span className="font-display font-bold text-lg tracking-tight text-white">HUSTLE</span>
        </div>
        <div className="relative z-10 space-y-8">
          <div>
            <p className="text-[11px] uppercase tracking-[0.22em] text-amber-500/80 font-bold mb-5">Your Life. Your Game.</p>
            <h1 className="font-display font-bold text-white leading-[1.08] tracking-tight" style={{ fontSize: "clamp(2.4rem, 4vw, 3.8rem)" }}>
              TURN REAL LIFE<br />INTO YOUR GAME.
            </h1>
            <p className="mt-6 text-slate-400 text-base font-light leading-relaxed max-w-sm">
              Turn your goals into quests, build your character, and progress through your own world.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-px border border-white/5 rounded-xl overflow-hidden">
            {[
              { label: "QUESTS", sub: "Daily missions" },
              { label: "LEVELS", sub: "Real progress" },
              { label: "YOUR WORLD", sub: "5 regions" },
            ].map((item) => (
              <div key={item.label} className="bg-white/[0.02] p-4">
                <p className="text-xs font-bold text-amber-400 tracking-wider">{item.label}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">{item.sub}</p>
              </div>
            ))}
          </div>
        </div>
        <p className="text-[11px] text-slate-600 relative z-10">© 2026 HUSTLE · Your goals. Your quests. Your world.</p>
      </div>

      {/* RIGHT form panel */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 sm:px-12">
        <div className="flex lg:hidden items-center gap-3 mb-10">
          <HustleMark size={26} />
          <span className="font-display font-bold text-lg tracking-tight text-white">HUSTLE</span>
        </div>
        <div className="w-full max-w-sm">
          <div className="mb-8">
            <h2 className="font-display font-bold text-2xl text-white tracking-tight mb-1">
              {isRegister ? "Create Your Character" : "Welcome Back"}
            </h2>
            <p className="text-sm text-slate-500">
              {isRegister ? "Every great adventure starts with a decision." : "Continue your adventure where you left off."}
            </p>
          </div>
          <form onSubmit={submit} className="space-y-3">
            {isRegister && (
              <div>
                <label className="block text-[11px] uppercase tracking-wider text-slate-500 mb-1.5">Name</label>
                <input placeholder="Your display name" value={form.displayName} onChange={update("displayName")}
                  className="w-full bg-ink-900 border border-ink-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500/60 transition-colors" />
              </div>
            )}
            <div>
              <label className="block text-[11px] uppercase tracking-wider text-slate-500 mb-1.5">Username</label>
              <input placeholder="username" value={form.username} onChange={update("username")} required
                className="w-full bg-ink-900 border border-ink-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500/60 transition-colors" />
            </div>
            {isRegister && (
              <div>
                <label className="block text-[11px] uppercase tracking-wider text-slate-500 mb-1.5">Email</label>
                <input placeholder="you@example.com" type="email" value={form.email} onChange={update("email")} required
                  className="w-full bg-ink-900 border border-ink-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500/60 transition-colors" />
              </div>
            )}
            <div>
              <label className="block text-[11px] uppercase tracking-wider text-slate-500 mb-1.5">
                Password{isRegister ? " (min 8 chars)" : ""}
              </label>
              <input placeholder="••••••••" type="password" value={form.password} onChange={update("password")} required minLength={isRegister ? 8 : 1}
                className="w-full bg-ink-900 border border-ink-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500/60 transition-colors" />
            </div>
            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
                <p className="text-xs text-rose-400">{error}</p>
              </div>
            )}
            <button type="submit" disabled={busy}
              className="w-full mt-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed text-ink-950 text-sm font-bold py-3 rounded-lg transition-colors tracking-wide">
              {busy ? "Please wait…" : isRegister ? "CREATE CHARACTER" : "ENTER THE REALM"}
            </button>
          </form>
          <p className="text-center text-sm text-slate-500 mt-6">
            {isRegister ? "Already have a character?" : "New to HUSTLE?"}{" "}
            <button onClick={() => { setMode(isRegister ? "login" : "register"); setError(""); }}
              className="text-amber-400 hover:text-amber-300 font-medium transition-colors">
              {isRegister ? "Log in" : "Create your character"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
