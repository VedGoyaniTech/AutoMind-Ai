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
        background: "#F7F4ED",
        surface: "#FFFFFF",
        elevated: "#EFECE5",
        muted: "#E8E4DC",
        border: "#E2DDD6",
        primary: {
          50: "#fff7ed",
          100: "#ffedd5",
          500: "#c96a2b",
          600: "#b05a22",
          700: "#944819",
          DEFAULT: "#c96a2b",
        },
        accent: {
          amber: "#c96a2b",
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
