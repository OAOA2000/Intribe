/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5', // 靛蓝
        secondary: '#F59E0B', // 活力橙
        accent: '#10B981', // 薄荷绿
        glass: 'rgba(255, 255, 255, 0.7)',
      },
      borderRadius: {
        '2xl': '1.5rem',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
      },
    },
  },
  plugins: [],
}