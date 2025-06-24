import { defineStore } from 'pinia'
import { notesAPI } from '../services/api'  // ✅ 수정된 API 함수들 사용

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
        const response = await notesAPI.getAll()  // ✅ 수정된 API 사용

        // 응답 구조 확인
        console.log('📦 API 응답:', response.data)

        // 응답 데이터 구조에 맞게 추출
        if (response.data.notes) {
          this.notes = response.data.notes
        } else if (Array.isArray(response.data)) {
          this.notes = response.data
        } else {
          this.notes = []
        }

        console.log(`✅ ${this.notes.length}개 노트 로드됨`)
      } catch (error) {
        this.error = '노트를 불러오는데 실패했습니다.'
        console.error('노트 로드 에러:', error)

        // 개발 중에는 Mock 데이터 사용
        console.log('🔄 Mock 데이터로 대체')
        this.notes = []

        throw error
      } finally {
        this.loading = false
      }
    },

    // 특정 노트 가져오기
    async fetchNote(id) {
      this.loading = true
      this.error = null

      try {
        console.log(`🚀 노트 ${id} 요청 중...`)
        const response = await notesAPI.getById(id)  // ✅ 수정된 API 사용

        this.currentNote = response.data
        console.log(`✅ 노트 ${id} 로드됨:`, this.currentNote.title)
        return this.currentNote
      } catch (error) {
        this.error = '노트를 불러오는데 실패했습니다.'
        console.error('노트 상세 로드 에러:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 노트 생성
    async createNote(noteData) {
      this.loading = true
      this.error = null

      try {
        console.log('🚀 새 노트 생성 중...', noteData)
        const response = await notesAPI.create(noteData)  // ✅ 수정된 API 사용
        const newNote = response.data

        // 상태 업데이트
        this.notes.unshift(newNote)
        this.currentNote = newNote

        console.log('✅ 새 노트 생성됨:', newNote.title)
        return newNote
      } catch (error) {
        this.error = '노트 생성에 실패했습니다.'
        console.error('노트 생성 에러:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 노트 수정
    async updateNote(id, noteData) {
      this.loading = true
      this.error = null

      try {
        console.log(`🚀 노트 ${id} 수정 중...`, noteData)
        const response = await notesAPI.update(id, noteData)  // ✅ 수정된 API 사용
        const updatedNote = response.data

        // 상태 업데이트
        const index = this.notes.findIndex(note => note.id === id)
        if (index !== -1) {
          this.notes[index] = updatedNote
        }
        this.currentNote = updatedNote

        console.log('✅ 노트 수정됨:', updatedNote.title)
        return updatedNote
      } catch (error) {
        this.error = '노트 수정에 실패했습니다.'
        console.error('노트 수정 에러:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 노트 삭제
    async deleteNote(id) {
      this.loading = true
      this.error = null

      try {
        console.log(`🚀 노트 ${id} 삭제 중...`)
        await notesAPI.delete(id)  // ✅ 수정된 API 사용

        // 상태 업데이트
        this.notes = this.notes.filter(note => note.id !== id)
        if (this.currentNote && this.currentNote.id === id) {
          this.currentNote = null
        }

        console.log('✅ 노트 삭제됨:', id)
      } catch (error) {
        this.error = '노트 삭제에 실패했습니다.'
        console.error('노트 삭제 에러:', error)
        throw error
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
        const response = await notesAPI.search(query, useRag)  // ✅ 수정된 API 사용

        this.searchResults = response.data.results || response.data || []
        console.log(`✅ 검색 완료: ${this.searchResults.length}개 결과`)
        return this.searchResults
      } catch (error) {
        this.error = '검색에 실패했습니다.'
        console.error('검색 에러:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 태그 목록 가져오기
    async fetchTags() {
      try {
        console.log('🚀 태그 목록 요청 중...')
        const response = await notesAPI.getTags()  // ✅ 수정된 API 사용

        this.tags = response.data.tags || response.data || []
        console.log(`✅ ${this.tags.length}개 태그 로드됨`)
      } catch (error) {
        console.error('태그 로드 에러:', error)
        this.tags = []
      }
    },

    // 노트 통계 가져오기
    async fetchStats() {
      try {
        console.log('🚀 노트 통계 요청 중...')
        const response = await notesAPI.getStats()  // ✅ 수정된 API 사용

        console.log('✅ 노트 통계 로드됨:', response.data)
        return response.data
      } catch (error) {
        console.error('통계 로드 에러:', error)
        return null
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
      return this.notes.find(note => note.id === parseInt(id))
    },

    // 로컬 노트 업데이트 (optimistic update용)
    updateLocalNote(id, changes) {
      const note = this.notes.find(n => n.id === id)
      if (note) {
        Object.assign(note, changes)
      }
      if (this.currentNote && this.currentNote.id === id) {
        Object.assign(this.currentNote, changes)
      }
    },

    // 연결 테스트
    async testConnection() {
      try {
        console.log('🔄 백엔드 연결 테스트 중...')
        await notesAPI.getAll()
        console.log('✅ 백엔드 연결 성공')
        return true
      } catch (error) {
        console.error('❌ 백엔드 연결 실패:', error)
        return false
      }
    }
  }
})
