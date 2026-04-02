module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-bg': "#050816",
        'cyber-panel': "rgba(15,23,42,0.85)",
        'cyber-primary': "#22d3ee",
        'cyber-secondary': "#f472b6",
        'cyber-accent': "#a855f7",
      },
      boxShadow: {
        'neon-cyan': "0 0 20px rgba(34,211,238,0.8)",
        'neon-pink': "0 0 20px rgba(244,114,182,0.8)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
