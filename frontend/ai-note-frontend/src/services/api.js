import axios from 'axios'

// API 인스턴스 생성
const api = axios.create({
  baseURL: 'http://localhost:5000',
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
      // 서버 응답이 있는 경우
      const message = responseError.response.data?.message || responseError.response.data?.error || 'Unknown server error'
      responseError.message = message
    } else if (responseError.request) {
      // 요청은 보냈지만 응답이 없는 경우
      responseError.message = 'No response from server. Please check if the backend is running.'
    } else {
      // 기타 에러
      responseError.message = responseError.message || 'Unknown error occurred'
    }

    return Promise.reject(responseError)
  }
)

// ✅ 노트 관련 API
export const notesAPI = {
  // 노트 목록 조회
  getAll: (params = {}) => api.get('/api/', { params }),

  // 특정 노트 조회
  getById: (id) => api.get(`/api/${id}`),

  // 노트 생성
  create: (noteData) => {
    console.log('📝 새 노트 생성 시작:', noteData.title)
    return api.post('/api/', noteData)
  },

  // 노트 수정
  update: (id, noteData) => {
    console.log(`✏️ 노트 ${id} 수정 시작:`, noteData.title)
    return api.put(`/api/${id}`, noteData)
  },

  // ✅ updateContent 함수 추가 (이게 누락되어서 에러 발생했음!)
  updateContent: (id, data) => {
    console.log(`📝 노트 ${id} 내용 업데이트`)
    return api.put(`/api/${id}`, data)
  },

  // 노트 삭제
  delete: (id) => api.delete(`/api/${id}`),

  // 노트 검색 (RAG 지원)
  search: (query, useRag = false) => api.post('/api/search', {
    query,
    use_rag: useRag
  }),

  // 유사한 노트 찾기
  getSimilar: (id) => api.get(`/api/${id}/similar`),

  // 노트 연결 그래프
  getGraph: () => api.get('/api/graph'),

  // 검색 자동완성
  getSuggestions: (query) => api.get('/api/suggest', { params: { q: query } }),

  // 태그 목록 조회
  getTags: () => api.get('/api/tags'),

  // 노트 통계
  getStats: () => api.get('/api/stats')
}

// ✅ AI 채팅 관련 API
export const chatAPI = {
  // 기본 AI 채팅
  chat: (message) => api.post('/api/', { message }),

  // RAG 기반 채팅
  ragChat: (message, useNotes = true) => api.post('/api/rag', {
    message,
    use_notes: useNotes
  }),

  // Claude API 테스트
  test: () => api.get('/api/test'),

  // RAG 시스템 상태 확인
  ragStatus: () => api.get('/api/rag/status'),

  // RAG 인덱스 재구축
  rebuildIndex: () => api.post('/api/rag/rebuild'),

  // RAG 전용 검색
  ragSearch: (query, k = 5) => api.post('/api/rag/search', { query, k }),

  // RAG 인덱스 삭제
  clearIndex: () => api.delete('/api/rag/clear')
}

// ✅ 시스템 관련 API
export const systemAPI = {
  // 헬스 체크
  health: () => api.get('/health'),

  // 시스템 정보 (홈페이지)
  info: () => api.get('/'),

  // 디버그 - 라우트 목록
  debugRoutes: () => api.get('/debug/routes'),

  // 디버그 - 데이터베이스 상태
  debugDatabase: () => api.get('/debug/database'),

  // 디버그 - 샘플 노트 생성
  createSampleNotes: () => api.post('/debug/sample-notes'),

  // 유틸리티 - 마크다운 미리보기
  markdownPreview: (content) => api.post('/utils/markdown', { content }),

  // 시스템 설정 정보
  debugConfig: () => api.get('/debug/config'),

  // 활동 통계
  getActivity: () => api.get('/utils/activity'),

  // 날짜 범위 정보
  getDateRanges: () => api.get('/utils/date-ranges')
}

// ✅ 유틸리티 함수들
export const apiUtils = {
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

        // 지연 시간 대기
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
      }
    }
  },

  // 백엔드 엔드포인트 목록 확인
  async getEndpoints() {
    try {
      const response = await systemAPI.debugRoutes()
      console.log('📋 등록된 엔드포인트:', response.data)
      return response.data
    } catch (endpointError) {
      console.error('❌ 엔드포인트 조회 실패:', endpointError.message)
      return null
    }
  },

  // RAG 시스템 테스트
  async testRAG() {
    try {
      console.log('🧠 RAG 시스템 테스트 중...')

      // RAG 상태 확인
      const statusResponse = await chatAPI.ragStatus()
      console.log('RAG 상태:', statusResponse.data)

      if (!statusResponse.data.rag_status?.available) {
        console.warn('⚠️ RAG 시스템이 비활성화되어 있습니다')
        return false
      }

      // 간단한 RAG 검색 테스트
      const searchResponse = await chatAPI.ragSearch('테스트', 3)
      console.log('RAG 검색 결과:', searchResponse.data)

      console.log('✅ RAG 시스템 테스트 성공')
      return true

    } catch (ragError) {
      console.error('❌ RAG 시스템 테스트 실패:', ragError.message)
      return false
    }
  },

  // RAG 인덱스 관리
  async manageRAGIndex(action = 'status') {
    try {
      switch (action) {
        case 'status':
          return await chatAPI.ragStatus()
        case 'rebuild':
          console.log('🔄 RAG 인덱스 재구축 중...')
          return await chatAPI.rebuildIndex()
        case 'clear':
          console.log('🗑️ RAG 인덱스 삭제 중...')
          return await chatAPI.clearIndex()
        default:
          throw new Error(`Unknown action: ${action}`)
      }
    } catch (manageError) {
      console.error(`❌ RAG ${action} 실패:`, manageError.message)
      throw manageError
    }
  },

  // 단순화된 노트 생성
  async createNoteSimple(noteData) {
    try {
      console.log(`📝 새 노트 생성: "${noteData.title}"`)

      const response = await notesAPI.create(noteData)

      if (response.data?.success && response.data?.note?.id) {
        console.log(`✅ 노트 생성 성공 - ID: ${response.data.note.id}`)
        return response.data.note
      } else {
        throw new Error('노트 생성 응답에 ID가 없습니다')
      }

    } catch (createError) {
      console.error('❌ 노트 생성 실패:', createError.message)
      throw createError
    }
  },

  // 노트 생성 + 내용 업데이트 (기존 notes.js에서 사용하는 함수명)
  async createAndIndexNote(noteData) {
    try {
      console.log('🚀 노트 생성 + 내용 업데이트 시작')

      // 1. 먼저 기본 노트 생성
      const createResponse = await notesAPI.create({
        title: noteData.title || 'Untitled',
        content: noteData.content || '',
        tags: noteData.tags || []
      })

      if (!createResponse.data?.success || !createResponse.data?.note?.id) {
        throw new Error('노트 생성 실패')
      }

      const newNote = createResponse.data.note
      console.log(`✅ 노트 생성 성공 - ID: ${newNote.id}`)

      // 2. 추가 내용이 있다면 업데이트
      if (noteData.content && noteData.content !== newNote.content) {
        console.log(`🔄 노트 ${newNote.id} 내용 업데이트 중...`)

        const updateResponse = await notesAPI.updateContent(newNote.id, {
          title: noteData.title || newNote.title,
          content: noteData.content,
          tags: noteData.tags || newNote.tags || []
        })

        if (updateResponse.data?.success) {
          console.log(`✅ 노트 ${newNote.id} 내용 업데이트 완료`)
          return updateResponse.data.note
        }
      }

      return newNote

    } catch (createIndexError) {
      console.error('❌ 노트 생성 + 업데이트 실패:', createIndexError.message)
      throw createIndexError
    }
  },

  // 전체 시스템 상태 확인
  async checkSystemHealth() {
    try {
      console.log('🏥 시스템 전체 상태 확인 중...')

      const results = {
        backend: false,
        database: false,
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

      // 2. 데이터베이스 확인
      try {
        await systemAPI.debugDatabase()
        results.database = true
        console.log('✅ 데이터베이스: 정상')
      } catch {
        console.log('❌ 데이터베이스: 연결 실패')
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
        const endpointsResponse = await systemAPI.debugRoutes()
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

// ✅ 통합 API 객체 (주요 기능만 포함)
const mainAPI = {
  // 노트 API
  ...notesAPI,

  // 채팅 API
  chat: chatAPI.chat,
  ragChat: chatAPI.ragChat,
  testChat: chatAPI.test,

  // RAG API
  ragStatus: chatAPI.ragStatus,
  ragRebuild: chatAPI.rebuildIndex,
  ragSearch: chatAPI.ragSearch,
  ragClear: chatAPI.clearIndex,

  // 시스템 API
  health: systemAPI.health,
  debugRoutes: systemAPI.debugRoutes,
  debugDatabase: systemAPI.debugDatabase,
  createSamples: systemAPI.createSampleNotes,

  // 유틸리티
  utils: apiUtils
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
export default mainAPI
