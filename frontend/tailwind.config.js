/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        civic: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc7fb',
          400: '#36abf7',
          500: '#0c90e7',
          600: '#0171c6',
          700: '#025aa1',
          800: '#064c85',
          900: '#0b406e',
          950: '#072949',
        }
      }
    },
  },
  plugins: [],
}
