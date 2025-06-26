// frontend/ai-note-frontend/src/stores/notes.js
// 기존 구조 유지, 버그 수정만 적용

import { defineStore } from 'pinia'
import { notesAPI, apiUtils } from '@/services/api'

export const useNotesStore = defineStore('notes', {
  state: () => ({
    notes: [],
    currentNote: null,
    loading: false,
    error: null,
    searchResults: [],
    tags: [],
    filter: {
      sortBy: 'updated_at',
      sortOrder: 'desc',
      searchQuery: ''
    }
  }),

  getters: {
    noteCount: (state) => state.notes.length,

    isLoading: (state) => state.loading,

    hasError: (state) => !!state.error,

    filteredNotes: (state) => {
      let filtered = [...state.notes]

      // 검색 필터
      if (state.filter.searchQuery) {
        const query = state.filter.searchQuery.toLowerCase()
        filtered = filtered.filter(note =>
          note.title.toLowerCase().includes(query) ||
          note.content.toLowerCase().includes(query) ||
          note.tags?.some(tag => tag.toLowerCase().includes(query))
        )
      }

      // 정렬
      const { sortBy, sortOrder } = state.filter
      filtered.sort((a, b) => {
        const order = sortOrder === 'asc' ? 1 : -1

        if (sortBy === 'title') {
          return a[sortBy].localeCompare(b[sortBy]) * order
        } else {
          return (new Date(a[sortBy]) - new Date(b[sortBy])) * order
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
    // ✅ 노트 목록 가져오기 - 올바른 응답 파싱
    async fetchNotes() {
      this.loading = true
      this.error = null

      try {
        console.log('🚀 노트 목록 요청 중...')
        const response = await notesAPI.getAll()

        console.log('📦 전체 응답:', response.data)

        // ✅ 올바른 응답 구조 파싱: response.data.data.notes
        if (response.data?.data?.notes) {
          this.notes = response.data.data.notes
          console.log(`✅ ${this.notes.length}개 노트 로드 성공!`)
        } else if (response.data?.notes) {
          // 백업 파싱
          this.notes = response.data.notes
          console.log(`✅ ${this.notes.length}개 노트 로드 성공! (백업 파싱)`)
        } else {
          console.warn('예상과 다른 응답 구조:', response.data)
          this.notes = []
        }

      } catch (error) {
        console.error('❌ 노트 로드 에러:', error)
        this.error = '노트 목록을 불러오는데 실패했습니다.'
        this.notes = []
        throw error
      } finally {
        this.loading = false
      }
    },

    // ✅ 특정 노트 가져오기 - 올바른 응답 파싱
    async fetchNote(id) {
      // ID 유효성 검사 강화
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

        console.log('📦 노트 응답:', response.data)

        // ✅ 올바른 응답 구조 파싱: response.data.data.note
        let note = null
        if (response.data?.data?.note) {
          note = response.data.data.note
        } else if (response.data?.note) {
          // 백업 파싱
          note = response.data.note
        } else {
          throw new Error('노트 데이터를 찾을 수 없습니다')
        }

        this.currentNote = note
        console.log(`✅ 노트 ${noteId} 로드됨:`, note.title)
        return note

      } catch (fetchNoteError) {
        this.error = '노트를 불러오는데 실패했습니다.'
        console.error('❌ 노트 상세 로드 에러:', fetchNoteError)
        throw fetchNoteError
      } finally {
        this.loading = false
      }
    },

    // ✅ 노트 생성 - 올바른 응답 파싱
    async createNote(noteData) {
      this.loading = true
      this.error = null

      try {
        console.log('🚀 새 노트 생성 중...', noteData)

        // ✅ 필수 필드 기본값 보장
        const noteToCreate = {
          title: noteData?.title?.trim() || 'Untitled',
          content: noteData?.content?.trim() || '',
          tags: Array.isArray(noteData?.tags) ? noteData.tags : []
        }

        // apiUtils.createAndIndexNote 사용 (이미 올바른 파싱 포함)
        const newNote = await apiUtils.createAndIndexNote(noteToCreate)

        // 상태 업데이트
        this.notes.unshift(newNote)
        this.currentNote = newNote

        console.log('✅ 새 노트 생성됨:', newNote.title, 'ID:', newNote.id)
        return newNote

      } catch (createError) {
        this.error = '노트 생성에 실패했습니다.'
        console.error('❌ 노트 생성 에러:', createError)
        throw createError
      } finally {
        this.loading = false
      }
    },

    // ✅ 노트 수정 - 올바른 응답 파싱
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

        // ✅ 필수 필드 기본값 보장
        const updateData = {
          title: noteData?.title?.trim() || 'Untitled',
          content: noteData?.content?.trim() || '',
          tags: Array.isArray(noteData?.tags) ? noteData.tags : []
        }

        const response = await notesAPI.update(noteId, updateData)

        // ✅ 올바른 응답 구조 파싱: response.data.data.note
        let updatedNote = null
        if (response.data?.data?.note) {
          updatedNote = response.data.data.note
        } else if (response.data?.note) {
          // 백업 파싱
          updatedNote = response.data.note
        } else {
          throw new Error('수정된 노트 데이터를 찾을 수 없습니다')
        }

        // 상태 업데이트
        const index = this.notes.findIndex(n => n.id === noteId)
        if (index !== -1) {
          this.notes[index] = updatedNote
        }
        this.currentNote = updatedNote

        console.log('✅ 노트 수정 완료:', updatedNote.title)
        return updatedNote

      } catch (updateError) {
        this.error = '노트 수정에 실패했습니다.'
        console.error('❌ 노트 수정 에러:', updateError)
        throw updateError
      } finally {
        this.loading = false
      }
    },

    // 노트 삭제
    async deleteNote(id) {
      if (!id) {
        throw new Error('노트 ID가 필요합니다')
      }

      this.loading = true
      this.error = null

      try {
        console.log(`🗑️ 노트 ${id} 삭제 중...`)

        await notesAPI.delete(id)

        // 상태에서 제거
        this.notes = this.notes.filter(note => note.id !== parseInt(id))

        // 현재 노트가 삭제된 노트면 초기화
        if (this.currentNote?.id === parseInt(id)) {
          this.currentNote = null
        }

        console.log('✅ 노트 삭제 완료')
        return true

      } catch (deleteError) {
        this.error = '노트 삭제에 실패했습니다.'
        console.error('❌ 노트 삭제 에러:', deleteError)
        throw deleteError
      } finally {
        this.loading = false
      }
    },

    // 노트 검색
    async searchNotes(query) {
      this.loading = true
      this.error = null

      try {
        console.log('🔍 노트 검색:', query)

        if (!query || query.trim() === '') {
          this.searchResults = []
          return []
        }

        const searchData = {
          query: query.trim(),
          limit: 50
        }

        const response = await notesAPI.search(searchData)

        // ✅ 응답 구조 파싱
        let results = []
        if (response.data?.data?.results) {
          results = response.data.data.results
        } else if (response.data?.results) {
          results = response.data.results
        } else if (Array.isArray(response.data)) {
          results = response.data
        }

        this.searchResults = results
        console.log(`✅ 검색 완료: ${results.length}개 결과`)
        return results

      } catch (searchError) {
        this.error = '노트 검색에 실패했습니다.'
        console.error('❌ 검색 에러:', searchError)
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

        // ✅ 응답 구조 파싱
        let tags = []
        if (response.data?.data?.tags) {
          tags = response.data.data.tags
        } else if (response.data?.tags) {
          tags = response.data.tags
        } else if (Array.isArray(response.data)) {
          tags = response.data
        }

        this.tags = tags
        console.log(`✅ ${tags.length}개 태그 로드됨`)
        return tags
      } catch (tagsError) {
        console.error('❌ 태그 로드 에러:', tagsError)
        this.tags = []
        return []
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
        console.error('❌ 통계 로드 에러:', statsError)
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
      } catch (testError) {
        console.error('❌ 연결 테스트 실패:', testError)
        return false
      }
    }
  }
})
