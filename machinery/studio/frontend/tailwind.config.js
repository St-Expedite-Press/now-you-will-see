/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Dark base palette
        canvas: '#0a0a0a',
        surface: '#111111',
        panel: '#181818',
        card: '#1e1e1e',
        border: '#2a2a2a',
        // Accent — green (cards/build mode)
        accent: {
          DEFAULT: '#40916c',
          hover: '#52b788',
          muted: '#1b4332',
        },
        // Agent — indigo
        agent: {
          DEFAULT: '#4f4f99',
          hover: '#6666bb',
          surface: '#1a1a38',
          text: '#9999ee',
        },
        // Text
        text: {
          primary: '#e8e8e8',
          secondary: '#a0a0a0',
          muted: '#606060',
        },
      },
      fontFamily: {
        mono: ['Courier New', 'Courier', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
