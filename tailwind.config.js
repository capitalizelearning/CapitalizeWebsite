/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './website/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'primary': "#002A14",
        'primary-light': "#E8E9E9",
        'text': '#191B1D',
        'text-light': '#8C8D8E',
        'accent': '#80ED99',
        'accent-light': '#80ED99',
        'accent-dark': '#2AC870',
      },
      fontFamily: {
        'sans': ['DM Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

