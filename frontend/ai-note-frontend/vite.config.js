import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // ✅ 프록시 설정 추가 - CORS 문제 해결
  server: {
    port: 5173,
    proxy: {
      // API 요청들을 백엔드로 프록시
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('프록시 에러:', err)
          })
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('프록시 요청:', req.method, req.url)
          })
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('프록시 응답:', proxyRes.statusCode, req.url)
          })
        }
      },
      // 헬스 체크
      '/health': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      // 디버그 엔드포인트들
      '/debug': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      // 유틸리티 엔드포인트들
      '/utils': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
      // ✅ 루트 경로(/) 프록시 제거 - Vue 앱이 로드되도록 함
    }
  },
  // 빌드 설정
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
