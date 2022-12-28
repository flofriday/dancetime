/** @type {import('tailwindcss').Config} */
const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  content: ["*.html"],
  theme: {
    fontFamily: {
      sans: ["IBM Plex Sans"],
      display: ["IBM Plex Sans"],
      body: ["IBM Plex Sans"],
    },
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", ...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [],
};
