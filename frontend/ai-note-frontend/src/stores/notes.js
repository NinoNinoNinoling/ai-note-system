import { defineStore } from 'pinia'
import { notesAPI, chatAPI, apiUtils } from '../services/api'

export const useNotesStore = defineStore('notes', {
  state: () => ({
    notes: [],
    currentNote: null,
    tags: [],
    searchResults: [],
    loading: false,
    error: null,
    filter: {
      search: '',
      tag: '',
      sortBy: 'updated_at', // created_at, updated_at, title
      sortOrder: 'desc' // asc, desc
    }
  }),

  getters: {
    // 노트 개수
    noteCount: (state) => state.notes.length,

    // 필터링된 노트 목록
    filteredNotes: (state) => {
      let filtered = [...state.notes]

      // 검색어 필터
      if (state.filter.search) {
        const searchTerm = state.filter.search.toLowerCase()
        filtered = filtered.filter(note =>
          note.title.toLowerCase().includes(searchTerm) ||
          note.content.toLowerCase().includes(searchTerm)
        )
      }

      // 태그 필터
      if (state.filter.tag) {
        filtered = filtered.filter(note =>
          note.tags && note.tags.includes(state.filter.tag)
        )
      }

      // 정렬
      filtered.sort((a, b) => {
        const field = state.filter.sortBy
        const order = state.filter.sortOrder === 'asc' ? 1 : -1

        if (field === 'title') {
          return a[field].localeCompare(b[field]) * order
        } else {
          return (new Date(a[field]) - new Date(b[field])) * order
        }
      })

      return filtered
    },

    // 노트 통계
    noteStats: (state) => ({
      total: state.notes.length,
      tags: state.tags.length,
      recentlyUpdated: state.notes.filter(note => {
        const dayAgo = new Date()
        dayAgo.setDate(dayAgo.getDate() - 1)
        return new Date(note.updated_at) > dayAgo
      }).length
    }),

    // 태그별 노트 개수
    tagCounts: (state) => {
      const counts = {}
      state.notes.forEach(note => {
        if (note.tags) {
          note.tags.forEach(tag => {
            counts[tag] = (counts[tag] || 0) + 1
          })
        }
      })
      return counts
    }
  },

  actions: {
    // 노트 목록 가져오기
    async fetchNotes() {
      this.loading = true
      this.error = null

      try {
        console.log('🚀 노트 목록 요청 중...')
        const response = await notesAPI.getAll()

        // ✅ 새 api.js 응답 구조에 맞게 수정
        console.log('📦 API 응답:', response.data)

        if (response.data?.success && response.data.notes) {
          this.notes = response.data.notes
        } else if (Array.isArray(response.data)) {
          this.notes = response.data
        } else {
          this.notes = []
        }

        console.log(`✅ ${this.notes.length}개 노트 로드됨`)
      } catch (fetchError) {
        this.error = '노트를 불러오는데 실패했습니다.'
        console.error('노트 로드 에러:', fetchError)
        this.notes = []
        throw fetchError
      } finally {
        this.loading = false
      }
    },

    // 특정 노트 가져오기
    async fetchNote(id) {
      // ✅ ID 유효성 검사 강화
      if (!id || id === 'undefined' || id === 'null' || id === 'new') {
        throw new Error(`잘못된 노트 ID: ${id}`)
      }

      const noteId = parseInt(id)
      if (isNaN(noteId)) {
        throw new Error(`숫자가 아닌 노트 ID: ${id}`)
      }

      this.loading = true
      this.error = null

      try {
        console.log(`🚀 노트 ${noteId} 요청 중...`)
        const response = await notesAPI.getById(noteId)

        // ✅ 새 api.js 응답 구조에 맞게 수정
        if (response.data?.success && response.data.note) {
          this.currentNote = response.data.note
        } else if (response.data?.note) {
          this.currentNote = response.data.note
        } else {
          this.currentNote = response.data
        }

        console.log(`✅ 노트 ${noteId} 로드됨:`, this.currentNote.title)
        return this.currentNote
      } catch (fetchNoteError) {
        this.error = '노트를 불러오는데 실패했습니다.'
        console.error('노트 상세 로드 에러:', fetchNoteError)
        throw fetchNoteError
      } finally {
        this.loading = false
      }
    },

    // ✅ 노트 생성 (새 api.js의 createAndIndexNote 사용)
    async createNote(noteData) {
      this.loading = true
      this.error = null

      try {
        console.log('🚀 새 노트 생성 중...', noteData)

        // ✅ 새 api.js의 apiUtils.createAndIndexNote 사용
        const newNote = await apiUtils.createAndIndexNote({
          title: noteData.title || 'Untitled',
          content: noteData.content || '',
          tags: Array.isArray(noteData.tags) ? noteData.tags : []
        })

        // 상태 업데이트
        this.notes.unshift(newNote)
        this.currentNote = newNote

        console.log('✅ 새 노트 생성됨:', newNote.title, 'ID:', newNote.id)
        return newNote
      } catch (createError) {
        this.error = '노트 생성에 실패했습니다.'
        console.error('노트 생성 에러:', createError)

        // ✅ 백업: 기본 API 시도 (새 api.js 구조 반영)
        try {
          console.log('🔄 기본 API로 재시도...')
          const response = await notesAPI.create({
            title: noteData.title || 'Untitled',
            content: noteData.content || '',
            tags: Array.isArray(noteData.tags) ? noteData.tags : []
          })

          let newNote
          if (response.data?.success && response.data.note) {
            newNote = response.data.note
          } else if (response.data?.note) {
            newNote = response.data.note
          } else {
            newNote = response.data
          }

          this.notes.unshift(newNote)
          this.currentNote = newNote
          console.log('✅ 기본 API로 노트 생성 성공:', newNote.id)
          return newNote

        } catch (backupError) {
          console.error('❌ 백업 생성도 실패:', backupError)
          throw createError
        }
      } finally {
        this.loading = false
      }
    },

    // 노트 수정
    async updateNote(id, noteData) {
      // ID 유효성 검사
      if (!id || id === 'undefined' || id === 'null') {
        throw new Error(`잘못된 노트 ID: ${id}`)
      }

      const noteId = parseInt(id)
      if (isNaN(noteId)) {
        throw new Error(`숫자가 아닌 노트 ID: ${id}`)
      }

      this.loading = true
      this.error = null

      try {
        console.log(`🚀 노트 ${noteId} 수정 중...`, noteData)

        const updateData = {
          title: noteData.title || 'Untitled',
          content: noteData.content || '',
          tags: Array.isArray(noteData.tags) ? noteData.tags : []
        }

        const response = await notesAPI.update(noteId, updateData)

        // ✅ 새 api.js 응답 구조에 맞게 수정
        let updatedNote
        if (response.data?.success && response.data.note) {
          updatedNote = response.data.note
        } else if (response.data?.note) {
          updatedNote = response.data.note
        } else {
          updatedNote = response.data
        }

        // 상태 업데이트
        const index = this.notes.findIndex(note => note.id === noteId)
        if (index !== -1) {
          this.notes[index] = updatedNote
        }
        this.currentNote = updatedNote

        console.log('✅ 노트 수정됨:', updatedNote.title)
        return updatedNote
      } catch (updateError) {
        this.error = '노트 수정에 실패했습니다.'
        console.error('노트 수정 에러:', updateError)
        throw updateError
      } finally {
        this.loading = false
      }
    },

    // 노트 삭제
    async deleteNote(id) {
      if (!id || id === 'undefined' || id === 'null') {
        throw new Error(`잘못된 노트 ID: ${id}`)
      }

      const noteId = parseInt(id)
      if (isNaN(noteId)) {
        throw new Error(`숫자가 아닌 노트 ID: ${id}`)
      }

      this.loading = true
      this.error = null

      try {
        console.log(`🚀 노트 ${noteId} 삭제 중...`)
        await notesAPI.delete(noteId)

        // 상태 업데이트
        this.notes = this.notes.filter(note => note.id !== noteId)
        if (this.currentNote && this.currentNote.id === noteId) {
          this.currentNote = null
        }

        console.log('✅ 노트 삭제됨:', noteId)
      } catch (deleteError) {
        this.error = '노트 삭제에 실패했습니다.'
        console.error('노트 삭제 에러:', deleteError)
        throw deleteError
      } finally {
        this.loading = false
      }
    },

    // 노트 검색
    async searchNotes(query, useRag = false) {
      this.loading = true
      this.error = null

      try {
        console.log(`🚀 검색 중: "${query}" (RAG: ${useRag})`)
        const response = await notesAPI.search(query, useRag)

        // ✅ 새 api.js 응답 구조에 맞게 수정
        if (response.data?.success && response.data.results) {
          this.searchResults = response.data.results
        } else if (response.data?.results) {
          this.searchResults = response.data.results
        } else if (Array.isArray(response.data)) {
          this.searchResults = response.data
        } else {
          this.searchResults = []
        }

        console.log(`✅ 검색 완료: ${this.searchResults.length}개 결과`)
        return this.searchResults
      } catch (searchError) {
        this.error = '검색에 실패했습니다.'
        console.error('검색 에러:', searchError)
        this.searchResults = []
        throw searchError
      } finally {
        this.loading = false
      }
    },

    // 태그 목록 가져오기
    async fetchTags() {
      try {
        console.log('🚀 태그 목록 요청 중...')
        const response = await notesAPI.getTags()

        // ✅ 새 api.js 응답 구조에 맞게 수정
        if (response.data?.success && response.data.tags) {
          this.tags = response.data.tags
        } else if (response.data?.tags) {
          this.tags = response.data.tags
        } else if (Array.isArray(response.data)) {
          this.tags = response.data
        } else {
          this.tags = []
        }

        console.log(`✅ ${this.tags.length}개 태그 로드됨`)
      } catch (tagsError) {
        console.error('태그 로드 에러:', tagsError)
        this.tags = []
      }
    },

    // 노트 통계 가져오기
    async fetchStats() {
      try {
        console.log('🚀 노트 통계 요청 중...')
        const response = await notesAPI.getStats()

        console.log('✅ 노트 통계 로드됨:', response.data)
        return response.data
      } catch (statsError) {
        console.error('통계 로드 에러:', statsError)
        return null
      }
    },

    // 유사한 노트 찾기
    async fetchSimilarNotes(id) {
      try {
        console.log(`🚀 노트 ${id} 유사 노트 요청 중...`)
        const response = await notesAPI.getSimilar(id)

        // ✅ 새 api.js 응답 구조에 맞게 수정
        const similarNotes = response.data?.similar || response.data?.results || response.data || []
        console.log(`✅ ${similarNotes.length}개 유사 노트 발견`)
        return similarNotes
      } catch (similarError) {
        console.error('유사 노트 조회 에러:', similarError)
        return []
      }
    },

    // 필터 설정
    setFilter(filterData) {
      this.filter = { ...this.filter, ...filterData }
    },

    // 현재 노트 설정
    setCurrentNote(note) {
      this.currentNote = note
    },

    // 에러 클리어
    clearError() {
      this.error = null
    },

    // 검색 결과 클리어
    clearSearchResults() {
      this.searchResults = []
    },

    // 캐시된 노트에서 찾기 (네트워크 요청 없이)
    getCachedNote(id) {
      const noteId = parseInt(id)
      return this.notes.find(note => note.id === noteId)
    },

    // 로컬 노트 업데이트 (optimistic update용)
    updateLocalNote(id, changes) {
      const noteId = parseInt(id)
      const note = this.notes.find(n => n.id === noteId)
      if (note) {
        Object.assign(note, changes)
      }
      if (this.currentNote && this.currentNote.id === noteId) {
        Object.assign(this.currentNote, changes)
      }
    },

    // 연결 테스트
    async testConnection() {
      try {
        console.log('🔄 백엔드 연결 테스트 중...')
        const isConnected = await apiUtils.checkConnection()
        console.log(`${isConnected ? '✅' : '❌'} 백엔드 연결 ${isConnected ? '성공' : '실패'}`)
        return isConnected
      } catch (connectionError) {
        console.error('❌ 백엔드 연결 실패:', connectionError)
        return false
      }
    },

    // 캐시 새로고침
    async refreshCache() {
      try {
        console.log('🔄 캐시 새로고침 중...')
        await Promise.all([
          this.fetchNotes(),
          this.fetchTags()
        ])
        console.log('✅ 캐시 새로고침 완료')
      } catch (refreshError) {
        console.error('❌ 캐시 새로고침 실패:', refreshError)
      }
    },

    // ✅ RAG 관련 액션들 (새 api.js에 맞춰서 수정)
    // RAG 상태 확인
    async checkRAGStatus() {
      try {
        const response = await chatAPI.ragStatus()
        return response.data
      } catch (ragStatusError) {
        console.error('RAG 상태 확인 실패:', ragStatusError)
        return null
      }
    },

    // RAG 인덱스 재구축
    async rebuildRAGIndex() {
      try {
        console.log('🔄 RAG 인덱스 재구축 시작...')
        const response = await chatAPI.rebuildIndex()
        console.log('✅ RAG 인덱스 재구축 완료')
        return response.data
      } catch (rebuildError) {
        console.error('❌ RAG 인덱스 재구축 실패:', rebuildError)
        throw rebuildError
      }
    },

    // ✅ 특정 노트 RAG 인덱싱 (실제 백엔드에는 없는 기능이므로 시뮬레이션)
    async indexNoteToRAG(noteId) {
      try {
        console.log(`📚 노트 ${noteId} RAG 인덱싱 시뮬레이션...`)

        // RAG 상태 확인으로 대체
        const ragStatus = await this.checkRAGStatus()

        const result = {
          indexed: ragStatus?.rag_status?.available || false,
          note_id: noteId,
          simulated: true
        }

        console.log(`✅ 노트 ${noteId} RAG 인덱싱 완료 (시뮬레이션)`)
        return result
      } catch (indexError) {
        console.error(`❌ 노트 ${noteId} RAG 인덱싱 실패:`, indexError)
        return {
          indexed: false,
          note_id: noteId,
          error: indexError.message
        }
      }
    },

    // ✅ 배치 RAG 인덱싱 (시뮬레이션)
    async batchIndexToRAG(noteIds = null) {
      try {
        const idsToIndex = noteIds || this.notes.map(note => note.id)
        console.log(`📚 배치 RAG 인덱싱 시뮬레이션 - ${idsToIndex.length}개 노트`)

        // RAG 상태 확인
        const ragStatus = await this.checkRAGStatus()
        const isAvailable = ragStatus?.rag_status?.available || false

        const result = {
          indexed_count: isAvailable ? idsToIndex.length : 0,
          total_count: idsToIndex.length,
          note_ids: idsToIndex,
          simulated: true
        }

        console.log('✅ 배치 RAG 인덱싱 완료 (시뮬레이션)')
        return result
      } catch (batchError) {
        console.error('❌ 배치 RAG 인덱싱 실패:', batchError)
        throw batchError
      }
    },

    // RAG 검색 (기존 search와 별도)
    async ragSearch(query, k = 5) {
      try {
        console.log(`🔍 RAG 검색: "${query}"`)
        const response = await chatAPI.ragSearch(query, k)

        const results = response.data?.results || []
        console.log(`✅ RAG 검색 완료: ${results.length}개 결과`)
        return response.data
      } catch (ragSearchError) {
        console.error('❌ RAG 검색 실패:', ragSearchError)
        throw ragSearchError
      }
    },

    // ✅ 새로 추가: 시스템 전체 상태 확인
    async checkSystemHealth() {
      try {
        const healthData = await apiUtils.checkSystemHealth()
        console.log('🏥 시스템 상태:', healthData)
        return healthData
      } catch (healthError) {
        console.error('❌ 시스템 상태 확인 실패:', healthError)
        return null
      }
    },

    // ✅ 새로 추가: RAG 시스템 테스트
    async testRAGSystem() {
      try {
        const testResult = await apiUtils.testRAG()
        console.log('🧠 RAG 테스트 결과:', testResult)
        return testResult
      } catch (ragTestError) {
        console.error('❌ RAG 테스트 실패:', ragTestError)
        return false
      }
    }
  }
})
