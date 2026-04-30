import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwind from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwind()],
  server: {
    port: 4005,
    host: true,
  },
  preview: {
    port: 4005,
    host: true,
  },
})
