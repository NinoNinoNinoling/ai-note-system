import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router/index.js'
import App from './App.vue'

// 스타일 import
import './style.css'

// API 연결 테스트 유틸리티
import { apiUtils } from './services/api'

// Vue 앱 생성
const app = createApp(App)

// Pinia 스토어 설정
const pinia = createPinia()
app.use(pinia)

// Vue Router 설정
app.use(router)

// 전역 속성 설정
app.config.globalProperties.$apiUtils = apiUtils

// 전역 에러 핸들러
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue 전역 에러:', err)
  console.error('컴포넌트 정보:', info)

  // 프로덕션에서는 에러 리포팅 서비스에 전송
  if (import.meta.env.PROD) {
    // 예: Sentry, LogRocket 등
    console.log('프로덕션 에러 리포팅:', { err, info })
  }
}

// 개발 모드에서만 성능 추적
if (import.meta.env.DEV) {
  app.config.performance = true
}

// 앱 초기화 및 마운트
const initializeApp = async () => {
  try {
    console.log('🚀 AI Note System 시작...')

    // 백엔드 연결 확인
    const isBackendConnected = await apiUtils.checkConnection()

    if (isBackendConnected) {
      console.log('✅ 백엔드 서버 연결 성공')
    } else {
      console.warn('⚠️ 백엔드 서버 연결 실패 - Mock 데이터 모드로 실행')

      // 사용자에게 알림
      setTimeout(() => {
        if (window.app && window.app.showNotification) {
          window.app.showNotification(
            'Backend server not available. Running in offline mode.',
            'warning'
          )
        }
      }, 1000)
    }

    // Vue 앱 마운트
    app.mount('#app')

    console.log('✅ Vue 앱 마운트 완료')

    // 개발 모드에서 디버그 정보 출력
    if (import.meta.env.DEV) {
      console.log('🔧 개발 모드 정보:')
      console.log('- Vue version:', app.version)
      console.log('- Router:', router)
      console.log('- Store:', pinia)
      console.log('- API base URL:', import.meta.env.VITE_API_URL || 'http://localhost:5000/api')
    }

  } catch (error) {
    console.error('❌ 앱 초기화 실패:', error)

    // 기본 에러 페이지 표시
    document.getElementById('app').innerHTML = `
      <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        font-family: system-ui, -apple-system, sans-serif;
        background: #f9fafb;
        color: #374151;
        text-align: center;
        padding: 2rem;
      ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">⚠️</div>
        <h1 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;">
          Failed to initialize AI Note System
        </h1>
        <p style="color: #6b7280; margin-bottom: 2rem;">
          ${error.message || 'Unknown error occurred'}
        </p>
        <button
          onclick="window.location.reload()"
          style="
            background: #3b82f6;
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 0.5rem;
            cursor: pointer;
            font-weight: 500;
          "
        >
          Reload Page
        </button>
      </div>
    `
  }
}

// 앱 초기화 실행
initializeApp()

// Hot Module Replacement (HMR) 지원
if (import.meta.hot) {
  import.meta.hot.accept()
}
