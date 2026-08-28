import { defineConfig } from 'vite'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const page = (name) => fileURLToPath(new URL(`./${name}.html`, import.meta.url))

// Multi-page application: every HTML file below is a real page with its own
// React root and its own entry point in src/entries/. Navigation between them
// is a plain browser navigation (<a href="/portfolios.html">), not client-side
// routing.
export default defineConfig({
  plugins: [react(), tailwindcss()],

  build: {
    rollupOptions: {
      input: {
        home: page('index'),
        login: page('login'),
        signup: page('signup'),
        portfolios: page('portfolios'),
        portfolio: page('portfolio'),
        profile: page('profile'),
      },
    },
  },

  server: {
    port: 5173,
    // The app always calls the API on a relative path (/api/...). In dev the
    // Vite server forwards those calls to FastAPI, so there is no API base URL
    // to configure anywhere in the UI.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
