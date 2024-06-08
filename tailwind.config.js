/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");

module.exports = {
  content: ["./templates/*.html"],
  theme: {
    extend: {},
    colors: {
      ...colors,

      stone: colors.warmGray,
      sky: colors.lightBlue,
      neutral: colors.trueGray,
      gray: colors.coolGray,
      slate: colors.blueGray,
    },
  },
  plugins: [],
};
