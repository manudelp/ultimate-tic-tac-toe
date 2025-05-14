module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1DA1F2",
        secondary: "#14171A",
      },
      boxShadow: {
        'glow': '0 0 15px rgba(59, 130, 246, 0.5)'
      },
    },
  },
  plugins: [],
};