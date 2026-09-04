/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aura: {
          bg: '#090A0F',        // Carbon Black
          surface: '#12141F',   // Deep Titanium Slate
          card: '#181B2A',      // Elevated Panel
          border: '#23273A',    // Cold Wireframe Line
          violet: '#7C3AED',    // Electric Ultraviolet
          iris: '#A78BFA',      // Soft Periwinkle / Iris
          crimson: '#EF4444',   // Conflict Hazard
          emerald: '#10B981',   // Cleared Baseline
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