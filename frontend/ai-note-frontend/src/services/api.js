// frontend/ai-note-frontend/src/services/api.js
// 실제 백엔드 엔드포인트에 맞게 수정된 버전

import axios from 'axios'

// API 인스턴스 생성 - 프록시 사용으로 baseURL 제거
const api = axios.create({
  baseURL: '', // ✅ 프록시 사용을 위해 빈 문자열로 변경
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
  (requestError) => {
    console.error('❌ 요청 에러:', requestError)
    return Promise.reject(requestError)
  }
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API 응답: ${response.status} ${response.config.url}`)
    return response
  },
  (responseError) => {
    console.error(`❌ API 에러: ${responseError.response?.status} ${responseError.config?.url}`)

    // 에러 메시지 표준화
    if (responseError.response) {
      const message = responseError.response.data?.message || responseError.response.data?.error || 'Unknown server error'
      responseError.message = message
    } else if (responseError.request) {
      responseError.message = 'No response from server. Please check if the backend is running.'
    } else {
      responseError.message = responseError.message || 'Unknown error occurred'
    }

    return Promise.reject(responseError)
  }
)

// ✅ 노트 관련 API - 실제 백엔드 엔드포인트에 맞게 수정
const notesAPI = {
  // 노트 목록 조회
  getAll: (params = {}) => api.get('/api/notes', { params }),

  // 특정 노트 조회
  getById: (id) => api.get(`/api/notes/${id}`),

  // 노트 생성
  create: (noteData) => {
    console.log('📝 새 노트 생성 시작:', noteData.title)
    return api.post('/api/notes', noteData)
  },

  // 노트 수정
  update: (id, noteData) => {
    console.log(`✏️ 노트 ${id} 수정 시작:`, noteData.title)
    return api.put(`/api/notes/${id}`, noteData)
  },

  // 노트 삭제
  delete: (id) => {
    console.log(`🗑️ 노트 ${id} 삭제 시작`)
    return api.delete(`/api/notes/${id}`)
  },

  // 노트 검색
  search: (searchData) => {
    console.log('🔍 노트 검색:', searchData.query)
    return api.post('/api/notes/search', searchData)
  },

  // 태그 목록 조회
  getTags: () => api.get('/api/notes/tags'),

  // 태그별 노트 조회
  getByTag: (tag) => api.get(`/api/notes/tags/${tag}`),

  // 최근 노트 조회
  getRecent: (limit = 10) => api.get('/api/notes/recent', { params: { limit } }),

  // 노트 통계
  getStats: () => api.get('/api/notes/stats'),

  // 노트 데이터 검증
  validate: (noteData) => api.post('/api/notes/validate', noteData)
}

// ✅ 채팅 관련 API - 실제 백엔드 엔드포인트에 맞게 수정
const chatAPI = {
  // 기본 AI 채팅
  chat: (message) => {
    console.log('💬 기본 채팅 요청:', message)
    return api.post('/api/', { message })
  },

  // RAG 기반 채팅
  ragChat: (message) => {
    console.log('🧠 RAG 채팅 요청:', message)
    return api.post('/api/rag', { message })
  },

  // Claude API 연결 테스트
  testClaude: () => api.get('/api/test'),

  // RAG 시스템 상태 확인
  ragStatus: () => api.get('/api/rag/status'),

  // RAG 인덱스 재구축
  ragRebuild: () => {
    console.log('🔄 RAG 인덱스 재구축 시작')
    return api.post('/api/rag/rebuild')
  },

  // 채팅 히스토리 조회
  getHistory: (limit = 50) => api.get('/api/history', { params: { limit } }),

  // 채팅 히스토리 검색
  searchHistory: (query, limit = 10) => {
    console.log('🔍 히스토리 검색:', query)
    return api.post('/api/history/search', { query, limit })
  },

  // 채팅 히스토리 삭제
  clearHistory: () => {
    console.log('🗑️ 채팅 히스토리 삭제')
    return api.delete('/api/history')
  },

  // 채팅 히스토리 내보내기
  exportHistory: (startDate, endDate) => {
    console.log('📤 히스토리 내보내기')
    return api.post('/api/history/export', { start_date: startDate, end_date: endDate })
  },

  // 채팅 요약 통계
  getSummary: (days = 7) => api.get('/api/history/summary', { params: { days } }),

  // 채팅 통계
  getStats: () => api.get('/api/stats'),

  // 고급 통계
  getAdvancedStats: () => api.get('/api/stats/advanced'),

  // API 엔드포인트 목록
  getEndpoints: () => api.get('/api/endpoints'),

  // 디버그 정보
  getDebugInfo: () => api.get('/api/debug/info')
}

// ✅ Multiple Chains API - 실제 백엔드 엔드포인트에 맞게 수정
const chainsAPI = {
  // 체인 정보 조회
  getInfo: () => api.get('/api/chains'),

  // 체인 상태 확인
  getStatus: () => api.get('/api/chains/status'),

  // 체인 테스트
  test: () => api.post('/api/chains/test'),

  // 노트 요약
  summarize: (data) => {
    console.log('📋 노트 요약 요청')
    return api.post('/api/summarize', data)
  },

  // 노트 분석
  analyze: (data) => {
    console.log('🔍 노트 분석 요청')
    return api.post('/api/analyze', data)
  },

  // 노트 개선 제안
  improve: (data) => {
    console.log('⚡ 노트 개선 요청')
    return api.post('/api/improve', data)
  },

  // 관련 노트 추천
  recommend: (data) => {
    console.log('💡 노트 추천 요청')
    return api.post('/api/recommend', data)
  },

  // 지식 공백 분석
  getKnowledgeGaps: () => api.get('/api/knowledge-gaps'),

  // 일괄 요약
  batchSummarize: (data) => {
    console.log('📋 일괄 요약 요청')
    return api.post('/api/batch/summarize', data)
  }
}

// ✅ 시스템 관련 API
const systemAPI = {
  // 헬스 체크
  health: () => api.get('/health'),

  // 홈 정보
  home: () => api.get('/'),

  // 라우트 정보 (디버그)
  debugRoutes: () => api.get('/debug/routes'),

  // 설정 정보 (디버그)
  debugConfig: () => api.get('/debug/config'),

  // 데이터베이스 정보 (디버그)
  debugDatabase: () => api.get('/debug/database'),

  // 샘플 노트 생성
  createSampleNotes: () => {
    console.log('📝 샘플 노트 생성 시작')
    return api.post('/debug/sample-notes')
  },

  // 활동 통계
  getActivityStats: () => api.get('/utils/activity'),

  // 날짜 범위 정보
  getDateRanges: () => api.get('/utils/date-ranges'),

  // 마크다운 미리보기
  markdownPreview: (content) => api.post('/utils/markdown', { content })
}

// ✅ 유틸리티 함수들
const apiUtils = {
  // 에러 메시지 추출
  getErrorMessage: (errorObj) => {
    if (errorObj.response?.data?.message) {
      return errorObj.response.data.message
    }
    if (errorObj.response?.data?.error) {
      return errorObj.response.data.error
    }
    return errorObj.message || 'Unknown error occurred'
  },

  // 성공 응답인지 확인
  isSuccess: (response) => {
    return response.status >= 200 && response.status < 300
  },

  // 백엔드 연결 상태 확인
  async checkConnection() {
    try {
      await systemAPI.health()
      console.log('✅ 백엔드 서버 연결 성공')
      return true
    } catch (connectionError) {
      console.warn('⚠️ 백엔드 서버 연결 실패:', connectionError.message)
      return false
    }
  },

  // API 재시도 함수
  async retry(apiCall, maxRetries = 3, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await apiCall()
      } catch (retryError) {
        console.warn(`🔄 API 재시도 ${i + 1}/${maxRetries}:`, retryError.message)

        if (i === maxRetries - 1) {
          throw retryError
        }

        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
      }
    }
  },

  // 노트 생성 + RAG 인덱싱 (통합 함수)
  async createAndIndexNote(noteData) {
    try {
      console.log('📝 노트 생성 + RAG 인덱싱 시작')

      // 1. 노트 생성
      const createResponse = await notesAPI.create(noteData)
      const newNote = createResponse.data.note || createResponse.data

      console.log('✅ 노트 생성됨:', newNote.title)

      // 2. RAG 인덱스 자동 재구축 (백엔드에서 자동으로 하지만 확실히 하기 위해)
      try {
        await chatAPI.ragRebuild()
        console.log('✅ RAG 인덱스 업데이트 완료')
      } catch (ragError) {
        console.warn('⚠️ RAG 인덱스 업데이트 실패 (노트는 생성됨):', ragError.message)
      }

      return newNote
    } catch (error) {
      console.error('❌ 노트 생성 실패:', error)
      throw error
    }
  },

  // 전체 시스템 상태 확인
  async checkSystemStatus() {
    try {
      console.log('🔍 시스템 상태 확인 중...')

      const results = {
        backend: false,
        database: false,
        claude: false,
        rag: false,
        endpoints: null
      }

      // 1. 백엔드 연결 확인
      try {
        await systemAPI.health()
        results.backend = true
        console.log('✅ 백엔드: 정상')
      } catch {
        console.log('❌ 백엔드: 연결 실패')
      }

      // 2. Claude API 확인
      try {
        const claudeResponse = await chatAPI.testClaude()
        results.claude = claudeResponse.data?.status === 'success'
        console.log(`${results.claude ? '✅' : '⚠️'} Claude API: ${results.claude ? '연결됨' : '연결 실패'}`)
      } catch {
        console.log('❌ Claude API: 테스트 실패')
      }

      // 3. RAG 시스템 확인
      try {
        const ragResponse = await chatAPI.ragStatus()
        results.rag = ragResponse.data?.rag_status?.available || false
        console.log(`${results.rag ? '✅' : '⚠️'} RAG: ${results.rag ? '활성화' : '비활성화'}`)
      } catch {
        console.log('❌ RAG: 상태 확인 실패')
      }

      // 4. 엔드포인트 목록 확인
      try {
        const endpointsResponse = await chatAPI.getEndpoints()
        results.endpoints = endpointsResponse.data
        console.log('✅ 엔드포인트: 정상')
      } catch {
        console.log('❌ 엔드포인트: 조회 실패')
      }

      console.log('🏁 시스템 상태 확인 완료:', results)
      return results

    } catch (healthError) {
      console.error('❌ 시스템 상태 확인 실패:', healthError.message)
      return null
    }
  }
}

// ✅ 통합 API 객체
const mainAPI = {
  // 노트 API
  notes: notesAPI,

  // 채팅 API
  chat: chatAPI,

  // 체인 API
  chains: chainsAPI,

  // 시스템 API
  system: systemAPI,

  // 유틸리티
  utils: apiUtils,

  // 자주 사용하는 기능들 (단축 접근)
  // 기본 채팅
  sendMessage: chatAPI.chat,
  // RAG 채팅
  sendRAGMessage: chatAPI.ragChat,
  // 노트 생성
  createNote: notesAPI.create,
  // 노트 목록
  getNotes: notesAPI.getAll,
  // 시스템 상태
  checkHealth: systemAPI.health
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
      content: "# AI 프로젝트 계획\n\n## LangChain 활용\n- RAG 시스템 구축\n- 문서 기반 QA\n\n## 기술 스택\n- Python + Flask\n- Vue.js\n- Claude API",
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
export const useMockData = false

// 기본 export
export default mainAPI

// 개별 export (필요시 개별 임포트 가능)
export { notesAPI, chatAPI, chainsAPI, systemAPI, apiUtils }
