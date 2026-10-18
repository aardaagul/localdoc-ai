import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// Geliştirme sırasında /api istekleri backend'e yönlendirilir; böylece CORS
// ayarıyla uğraşmak gerekmez. Hedef adres `VITE_PROXY_TARGET` ile değiştirilebilir
// (varsayılan: http://localhost:8000).
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', 'VITE_')
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
