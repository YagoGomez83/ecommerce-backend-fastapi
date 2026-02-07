import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Permite conexiones desde fuera del contenedor
    port: 5173,
    watch: {
      usePolling: true, // Necesario para hot-reload en Docker
    },
    hmr: {
      host: 'localhost', // Para que el HMR funcione correctamente
    },
  },
})
