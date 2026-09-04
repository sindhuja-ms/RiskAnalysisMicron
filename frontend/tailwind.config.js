/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        fab: {
          obsidian: '#0B0E14',   // Deep Cleanroom Base
          surface: '#121824',    // Card & Panel Surface
          card: '#182030',       // Interactive Elevation
          border: '#263044',     // Substrate Border Lines
          amber: '#F59E0B',      // Photolithography Yellow/Amber
          gold: '#FBBF24',       // Warm Accent Gold
          crimson: '#F43F5E',    // Statutory Conflict Red
          emerald: '#10B981',    // Cleared / Safe Baseline
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif']
      }
    },
  },
  plugins: [],
}