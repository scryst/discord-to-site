/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'coffee-brown': '#6F4E37',
        'coffee-light': '#A67C52',
        'coffee-dark': '#3C2A21',
      },
    },
  },
  plugins: [],
}
