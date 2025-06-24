import axios from 'axios'

// API 인스턴스 생성
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API 요청: ${config.method.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ 요청 에러:', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API 응답: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error(`❌ API 에러: ${error.response?.status} ${error.config?.url}`)

    // 에러 메시지 표준화
    if (error.response) {
      // 서버 응답이 있는 경우
      const message = error.response.data?.message || error.response.data?.error || 'Unknown server error'
      error.message = message
    } else if (error.request) {
      // 요청은 보냈지만 응답이 없는 경우
      error.message = 'No response from server. Please check if the backend is running.'
    } else {
      // 기타 에러
      error.message = error.message || 'Unknown error occurred'
    }

    return Promise.reject(error)
  }
)

// 노트 관련 API
export const notesAPI = {
  // 노트 목록 조회
  getAll: () => api.get('/notes'),

  // 특정 노트 조회
  getById: (id) => api.get(`/notes/${id}`),

  // 노트 생성
  create: (noteData) => api.post('/notes', noteData),

  // 노트 수정
  update: (id, noteData) => api.put(`/notes/${id}`, noteData),

  // 노트 삭제
  delete: (id) => api.delete(`/notes/${id}`),

  // 노트 검색
  search: (query, useRag = false) => api.post('/notes/search', {
    query,
    use_rag: useRag
  }),

  // 태그 목록 조회
  getTags: () => api.get('/notes/tags'),

  // 노트 통계
  getStats: () => api.get('/notes/stats')
}

// AI 채팅 관련 API
export const chatAPI = {
  // 기본 AI 채팅
  chat: (message) => api.post('/chat', { message }),

  // RAG 기반 채팅
  ragChat: (message, useNotes = true) => api.post('/chat/rag', {
    message,
    use_notes: useNotes
  }),

  // Claude API 테스트
  test: () => api.get('/chat/test'),

  // 채팅 히스토리 조회
  getHistory: () => api.get('/chat/history'),

  // RAG 인덱스 재구축
  rebuildIndex: () => api.post('/chat/rag/rebuild')
}

// 시스템 관련 API
export const systemAPI = {
  // 헬스 체크
  health: () => api.get('/health'),

  // 시스템 정보
  info: () => api.get('/info'),

  // 시스템 상태
  status: () => api.get('/')
}

// 유틸리티 함수들
export const apiUtils = {
  // 에러 메시지 추출
  getErrorMessage: (error) => {
    if (error.response?.data?.message) {
      return error.response.data.message
    }
    if (error.response?.data?.error) {
      return error.response.data.error
    }
    return error.message || 'Unknown error occurred'
  },

  // 성공 응답인지 확인
  isSuccess: (response) => {
    return response.status >= 200 && response.status < 300
  },

  // 백엔드 연결 상태 확인
  async checkConnection() {
    try {
      await systemAPI.health()
      return true
    } catch (error) {
      console.warn('⚠️ 백엔드 서버 연결 실패:', error.message)
      return false
    }
  },

  // API 재시도 함수
  async retry(apiCall, maxRetries = 3, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await apiCall()
      } catch (error) {
        console.warn(`🔄 API 재시도 ${i + 1}/${maxRetries}:`, error.message)

        if (i === maxRetries - 1) {
          throw error
        }

        // 지연 시간 대기
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
      }
    }
  }
}

// Mock 데이터 (개발/테스트용)
export const mockData = {
  notes: [
    {
      id: 1,
      title: "Vue.js 학습 노트",
      content: "# Vue.js 기초\n\n## Composition API\n- ref(), reactive()\n- computed, watch\n\n## 주요 개념\n- Component\n- Props & Emit\n- Lifecycle",
      tags: ["vue", "frontend", "javascript"],
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-16T14:30:00Z"
    },
    {
      id: 2,
      title: "AI 프로젝트 아이디어",
      content: "# AI 프로젝트 계획\n\n## LangChain 활용\n- RAG 시스템 구축\n- 문서 기반 QA\n\n## 기술 스택\n- Python + Flask\n- Vue.js\n- OpenAI API",
      tags: ["ai", "langchain", "project"],
      created_at: "2024-01-14T09:15:00Z",
      updated_at: "2024-01-16T11:20:00Z"
    }
  ],

  tags: ["vue", "frontend", "javascript", "ai", "langchain", "project", "python", "flask"],

  chatHistory: [
    {
      id: 1,
      message: "Vue.js에서 상태 관리는 어떻게 하나요?",
      response: "Vue.js에서는 여러 상태 관리 방법이 있습니다:\n\n1. **Pinia** (권장)\n2. Vuex (레거시)\n3. Composables\n\n각각의 장단점을 설명드리겠습니다...",
      timestamp: "2024-01-16T15:30:00Z"
    }
  ]
}

// 개발 모드 확인
export const isDevelopment = import.meta.env.DEV

// Mock 모드 설정 (백엔드가 없을 때 사용)
export const useMockData = false // true로 설정하면 Mock 데이터 사용

// 기본 export
export default api
