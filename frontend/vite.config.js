import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/agents': 'http://localhost:8000',
      '/workflows': 'http://localhost:8000',
      '/tools': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/ready': 'http://localhost:8000',
      '/info': 'http://localhost:8000',
      '/token': 'http://localhost:8000',
    },
  },
})
