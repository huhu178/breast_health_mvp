import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    allowedHosts: ['jiejie.online', 'www.jiejie.online'],
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        credentials: true
      }
    }
  }
})
