/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#090a0f", // Deep charcoal black foundation
          900: "#101118", // Rich surface base
          850: "#161822", // Elevated section
          800: "#1e202d", // Interactive hover surface
          750: "#252838", // Subtle contrast surface
          700: "#2e3246", // Hairline border
          650: "#393e56", // Defined border
          600: "#484e6c", // Subtle dividers & icons
        },
        arcane: {
          400: "#fbbf24", // Gold/Amber highlight
          500: "#f59e0b", // Rich amber
          600: "#d97706", // Dark amber
        },
        crimson: {
          400: "#f43f5e",
          500: "#e11d48",
          600: "#be123c",
        },
        emerald: {
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
        },
      },
      fontFamily: {
        display: ["'Outfit'", "'Cinzel'", "sans-serif"],
        serifDisplay: ["'Cinzel'", "serif"],
        body: ["'Plus Jakarta Sans'", "'Inter'", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        subtle: "0 1px 3px 0 rgba(0, 0, 0, 0.3)",
        card: "0 4px 20px -2px rgba(0, 0, 0, 0.4)",
        glow: "0 0 25px rgba(245, 158, 11, 0.12)",
        crimsonGlow: "0 0 25px rgba(225, 29, 72, 0.15)",
      },
    },
  },
  plugins: [],
};

