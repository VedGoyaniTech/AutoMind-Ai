/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#E8DCC6", // MochaCream
        surface: "#FAF7F2",    // Warm Soft Surface
        elevated: "#DFD2BA",   // Elevated MochaCream
        muted: "#B7A89A",      // CosmicLatte
        border: "#B7A89A",     // CosmicLatte
        cosmic: "#B7A89A",     // CosmicLatte
        mocha: "#E8DCC6",      // MochaCream
        burgundy: {
          DEFAULT: "#722F37",  // DeepBurgundy
          hover: "#58242A",
          light: "#8E3E47",
          50: "#FAF0F1",
          100: "#F5DFE1",
          500: "#722F37",
          600: "#58242A",
          700: "#431A20",
        },
        primary: {
          50: "#FAF0F1",
          100: "#F5DFE1",
          500: "#722F37",
          600: "#58242A",
          700: "#431A20",
          DEFAULT: "#722F37", // DeepBurgundy
        },
        accent: {
          burgundy: "#722F37",
          amber: "#722F37",
          emerald: "#10b981",
          blue: "#2563eb",
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        }
      }
    },
  },
  plugins: [],
}
