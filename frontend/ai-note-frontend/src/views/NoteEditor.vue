<template>
  <div class="note-editor h-screen bg-gray-50 flex flex-col">
    <!-- 상단 툴바 -->
    <div class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <router-link
          to="/notes"
          class="text-gray-500 hover:text-gray-700 flex items-center space-x-1"
        >
          <span>←</span>
          <span>Notes</span>
        </router-link>

        <div class="text-gray-300">|</div>

        <h1 class="text-lg font-medium text-gray-900">
          {{ editorMode === 'new' ? 'New Note' : 'Edit Note' }}
        </h1>
      </div>

      <div class="flex items-center space-x-3">
        <!-- 뷰 모드 토글 -->
        <div class="flex items-center bg-gray-100 rounded-lg p-1">
          <button
            @click="setViewMode('edit')"
            :class="[
              'px-3 py-1.5 rounded-md text-sm font-medium transition-colors view-mode-toggle',
              viewMode === 'edit'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            ]"
            title="Edit Only (Ctrl+1)"
          >
            📝 Edit
          </button>
          <button
            @click="setViewMode('split')"
            :class="[
              'px-3 py-1.5 rounded-md text-sm font-medium transition-colors view-mode-toggle',
              viewMode === 'split'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            ]"
            title="Split View (Ctrl+2)"
          >
            🔄 Split
          </button>
          <button
            @click="setViewMode('preview')"
            :class="[
              'px-3 py-1.5 rounded-md text-sm font-medium transition-colors view-mode-toggle',
              viewMode === 'preview'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            ]"
            title="Preview Only (Ctrl+3)"
          >
            👁️ Preview
          </button>
        </div>

        <!-- 저장 상태 -->
        <div v-if="viewMode !== 'preview'" class="flex items-center space-x-2 text-sm text-gray-500">
          <span v-if="saving" class="flex items-center space-x-1">
            <div class="animate-spin w-3 h-3 border border-blue-500 border-t-transparent rounded-full"></div>
            <span>Saving...</span>
          </span>
          <span v-else-if="autoSavePending" class="text-orange-500 flex items-center space-x-1">
            <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
            <span>Will save in {{ Math.max(0, autoSaveCountdown) }}s...</span>
          </span>
          <span v-else-if="lastSaved" class="text-green-600">
            ✅ Saved {{ formatLastSaved(lastSaved) }}
          </span>
          <span v-else-if="hasUnsavedChanges" class="text-orange-600">
            ● Unsaved changes
          </span>
        </div>

        <!-- 액션 버튼들 -->
        <div class="flex items-center space-x-2">
          <button
            v-if="viewMode !== 'preview'"
            @click="handleSave"
            :disabled="saving || !hasUnsavedChanges"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            💾 Save
          </button>

          <button
            v-if="editorMode === 'edit'"
            @click="handleDelete"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            🗑️ Delete
          </button>

          <!-- Preview 모드일 때 추가 버튼 -->
          <button
            v-if="viewMode === 'preview'"
            @click="setViewMode('edit')"
            class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            ✏️ Edit
          </button>
        </div>
      </div>
    </div>

    <!-- 메인 에디터 영역 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 에디터 패널 -->
      <div
        v-if="viewMode === 'edit' || viewMode === 'split'"
        :class="[
          'bg-white flex flex-col',
          viewMode === 'split' ? 'w-1/2 border-r border-gray-200' : 'w-full'
        ]"
      >
        <!-- 제목 입력 -->
        <div class="p-6 border-b border-gray-100">
          <input
            ref="titleInput"
            v-model="note.title"
            placeholder="Untitled"
            class="w-full text-2xl font-bold text-gray-900 placeholder-gray-400 border-none outline-none resize-none bg-transparent"
            @keydown.enter.prevent="focusContent"
            @input="markAsChanged"
          />
        </div>

        <!-- 태그 입력 -->
        <div class="px-6 py-3 border-b border-gray-100">
          <div class="flex flex-wrap gap-2 mb-2" v-if="note.tags && note.tags.length > 0">
            <span
              v-for="(tag, index) in note.tags"
              :key="tag"
              class="inline-flex items-center space-x-1 px-2.5 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
            >
              <span>#{{ tag }}</span>
              <button
                @click="removeTag(index)"
                class="text-blue-600 hover:text-blue-800 ml-1"
              >
                ×
              </button>
            </span>
          </div>

          <input
            v-model="newTag"
            placeholder="Add tags... (press Enter)"
            class="w-full text-sm text-gray-600 placeholder-gray-400 border-none outline-none bg-transparent"
            @keydown.enter.prevent="addTag"
            @keydown="handleTagInput"
            @input="markAsChanged"
          />
        </div>

        <!-- 마크다운 에디터 -->
        <div class="flex-1 relative">
          <textarea
            ref="contentTextarea"
            v-model="note.content"
            placeholder="Start writing your note in Markdown...

## Markdown Examples
- **Bold text**
- *Italic text*
- `Code`
- [Link](url)
- [[Note Link]]
- #hashtag

Press Ctrl+S to save"
            class="w-full h-full p-6 text-gray-900 placeholder-gray-400 border-none outline-none resize-none font-mono text-sm leading-relaxed bg-transparent"
            @input="handleContentChange"
            @keydown="handleKeydown"
          ></textarea>

          <!-- 마크다운 힌트 -->
          <div class="absolute bottom-4 right-4 text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">
            <div><kbd class="bg-gray-200 px-1 rounded">Ctrl+S</kbd> to save</div>
            <div class="mt-1"><kbd class="bg-gray-200 px-1 rounded">Ctrl+1,2,3</kbd> view modes</div>
          </div>
        </div>
      </div>

      <!-- 미리보기 패널 -->
      <div
        v-if="viewMode === 'split' || viewMode === 'preview'"
        :class="[
          'bg-white overflow-y-auto',
          viewMode === 'split' ? 'w-1/2' : 'w-full'
        ]"
      >
        <!-- Preview Only 모드일 때 상단 정보 -->
        <div v-if="viewMode === 'preview'" class="border-b border-gray-100 p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <h2 class="text-lg font-medium text-gray-900">Preview Mode</h2>
              <span class="text-sm text-gray-500">Read-only view</span>
            </div>
            <div class="flex items-center space-x-2 text-sm text-gray-500">
              <span>{{ wordCount }} words</span>
              <span>{{ characterCount }} characters</span>
            </div>
          </div>
        </div>

        <div class="p-6">
          <!-- 미리보기 제목 -->
          <h1 class="text-2xl font-bold text-gray-900 mb-4">
            {{ note.title || 'Untitled' }}
          </h1>

          <!-- 미리보기 태그 -->
          <div v-if="note.tags && note.tags.length > 0" class="flex flex-wrap gap-2 mb-6">
            <span
              v-for="tag in note.tags"
              :key="tag"
              class="inline-flex items-center px-2.5 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
            >
              #{{ tag }}
            </span>
          </div>

          <!-- 미리보기 내용 -->
          <div
            class="prose prose-gray max-w-none"
            v-html="renderedContent"
          ></div>
        </div>
      </div>
    </div>

    <!-- 하단 상태바 -->
    <div class="bg-gray-100 border-t border-gray-200 px-6 py-2 flex items-center justify-between text-xs text-gray-500">
      <div class="flex items-center space-x-4">
        <span>{{ wordCount }} words</span>
        <span>{{ characterCount }} characters</span>
        <span v-if="note.updated_at">Last modified: {{ formatDate(note.updated_at) }}</span>
        <span class="text-blue-600 font-medium">{{ getViewModeLabel() }}</span>
      </div>

      <div class="flex items-center space-x-4">
        <span>Markdown</span>
        <span>Auto-save: {{ autoSave ? 'On' : 'Off' }}</span>
        <span class="text-gray-400">Ctrl+1,2,3: View modes</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNotesStore } from '../stores/notes'

const router = useRouter()
const route = useRoute()
const notesStore = useNotesStore()

// 템플릿 참조
const titleInput = ref(null)
const contentTextarea = ref(null)

// 에디터 모드 및 상태
const editorMode = ref('unknown') // 'new' | 'edit' | 'unknown'
const currentNoteId = ref(null)

// 노트 상태
const note = ref({
  id: null,
  title: '',
  content: '',
  tags: []
})

const originalNote = ref({})
const newTag = ref('')
const showPreview = ref(false)
const viewMode = ref('edit') // 'edit', 'split', 'preview'
const saving = ref(false)
const lastSaved = ref(null)
const autoSave = ref(true)
const autoSaveTimeout = ref(null)
const autoSavePending = ref(false)
const autoSaveCountdown = ref(3)
const countdownInterval = ref(null)

// 컴퓨티드
const hasUnsavedChanges = computed(() =>
  JSON.stringify(note.value) !== JSON.stringify(originalNote.value)
)

const wordCount = computed(() => {
  if (!note.value.content) return 0
  return note.value.content.split(/\s+/).filter(word => word.length > 0).length
})

const characterCount = computed(() => {
  return note.value.content ? note.value.content.length : 0
})

const renderedContent = computed(() => {
  if (!note.value.content) return '<p class="text-gray-400">Start writing to see preview...</p>'

  // 간단한 마크다운 렌더링
  let html = note.value.content
    // 헤더
    .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-6 mb-3">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mt-8 mb-4">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-8 mb-4">$1</h1>')
    // 굵은글씨
    .replace(/\*\*(.*)\*\*/g, '<strong class="font-semibold">$1</strong>')
    // 기울임
    .replace(/\*(.*)\*/g, '<em class="italic">$1</em>')
    // 인라인 코드
    .replace(/`([^`]*)`/g, '<code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">$1</code>')
    // 링크
    .replace(/\[([^\]]*)\]\(([^)]*)\)/g, '<a href="$2" class="text-blue-600 hover:underline">$1</a>')
    // 노트 링크
    .replace(/\[\[([^\]]*)\]\]/g, '<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded">🔗 $1</span>')
    // 태그
    .replace(/#(\w+)/g, '<span class="text-blue-600 font-medium">#$1</span>')
    // 줄바꿈
    .replace(/\n/g, '<br>')

  return html
})

// 에디터 모드 결정
const determineEditorMode = () => {
  const routeId = route.params.id
  const routeName = route.name
  const routePath = route.path

  // 새 노트 판단
  if (routeName === 'NewNote' || routePath === '/notes/new' || routeId === 'new') {
    editorMode.value = 'new'
    currentNoteId.value = null
    return true
  }

  // 편집 모드 판단
  if (routeId && !isNaN(parseInt(routeId))) {
    const numericId = parseInt(routeId)
    editorMode.value = 'edit'
    currentNoteId.value = numericId
    return true
  }

  if (routeName === 'EditNote' && routeId) {
    const numericId = parseInt(routeId)
    if (!isNaN(numericId)) {
      editorMode.value = 'edit'
      currentNoteId.value = numericId
      return true
    }
  }

  // 모든 방법 실패
  console.error('알 수 없는 라우트 형태:', { name: routeName, path: routePath, id: routeId })
  editorMode.value = 'error'
  return false
}

// 새 노트 초기화
const initializeNewNote = () => {
  note.value = {
    id: null,
    title: '',
    content: '',
    tags: []
  }

  originalNote.value = JSON.parse(JSON.stringify(note.value))

  // 제목 입력에 포커스
  nextTick(() => {
    titleInput.value?.focus()
  })
}

// 기존 노트 로드
const loadExistingNote = async () => {
  try {
    const loadedNote = await notesStore.fetchNote(currentNoteId.value)
    note.value = { ...loadedNote }
    originalNote.value = JSON.parse(JSON.stringify(loadedNote))
  } catch (loadError) {
    console.error('노트 로드 실패:', loadError)
    alert('노트를 불러올 수 없습니다.')
    router.push('/notes')
  }
}

// 메인 초기화 함수
const initializeEditor = async () => {
  if (!determineEditorMode()) {
    router.push('/notes')
    return
  }

  if (editorMode.value === 'new') {
    initializeNewNote()
  } else if (editorMode.value === 'edit') {
    await loadExistingNote()
  }
}

// ✅ 간단한 저장 처리 (중복 방지 + 에러 핸들링)
const handleSave = async () => {
  // 🛡️ 중복 실행 완전 차단
  if (saving.value) {
    console.log('🚫 이미 저장 중이므로 무시')
    return
  }

  // 🛡️ 자동저장 타이머 즉시 취소
  if (autoSaveTimeout.value) {
    clearTimeout(autoSaveTimeout.value)
    autoSaveTimeout.value = null
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }
  autoSavePending.value = false

  // 🛡️ 저장 상태 즉시 설정
  saving.value = true

  console.log(`💾 저장 시작 - 모드: ${editorMode.value}, ID: ${currentNoteId.value}`)

  try {
    let savedNote

    if (editorMode.value === 'new') {
      // ✅ 새 노트 생성
      console.log('🚀 새 노트 생성 중...')

      const noteData = {
        title: note.value.title || 'Untitled',
        content: note.value.content || '',
        tags: note.value.tags || []
      }

      savedNote = await notesStore.createNote(noteData)

      if (!savedNote || !savedNote.id) {
        throw new Error('노트 생성 실패: 유효하지 않은 응답')
      }

      console.log(`✅ 새 노트 생성 완료: ${savedNote.id}`)

      // 🛡️ 상태 먼저 업데이트
      note.value = { ...savedNote }
      originalNote.value = JSON.parse(JSON.stringify(savedNote))

      // 편집 모드로 전환
      editorMode.value = 'edit'
      currentNoteId.value = savedNote.id

      // 🛡️ 라우트 변경
      await router.replace(`/notes/${savedNote.id}`)

    } else if (editorMode.value === 'edit') {
      // ✅ 기존 노트 수정
      console.log(`🔄 기존 노트 ${currentNoteId.value} 수정 중...`)

      const noteData = {
        title: note.value.title || 'Untitled',
        content: note.value.content || '',
        tags: note.value.tags || []
      }

      savedNote = await notesStore.updateNote(currentNoteId.value, noteData)

      if (!savedNote || !savedNote.id) {
        throw new Error('노트 수정 실패: 유효하지 않은 응답')
      }

      console.log(`✅ 기존 노트 수정 완료: ${savedNote.id}`)

      // 상태 업데이트
      note.value = { ...savedNote }
      originalNote.value = JSON.parse(JSON.stringify(savedNote))
    }

    lastSaved.value = new Date()

  } catch (saveError) {
    console.error('❌ 노트 저장 실패:', saveError.message)

    // 🚨 에러 타입별 처리
    if (saveError.message.includes('같은 노트가 최근에 생성되었습니다')) {
      alert('중복 저장 방지: 같은 노트가 최근에 생성되었습니다. 잠시 후 다시 시도해주세요.')
    } else if (saveError.message.includes('Network Error') || saveError.message.includes('timeout')) {
      alert('네트워크 연결을 확인하고 다시 시도해주세요.')
    } else {
      alert(`저장 실패: ${saveError.message}`)
    }
  } finally {
    // 🛡️ 반드시 저장 상태 해제
    saving.value = false
    console.log('💾 저장 프로세스 완료')
  }
}

const handleDelete = async () => {
  if (editorMode.value !== 'edit') return

  if (confirm(`"${note.value.title || 'Untitled'}"를 삭제하시겠습니까?`)) {
    try {
      await notesStore.deleteNote(currentNoteId.value)
      router.push('/notes')
    } catch (deleteError) {
      console.error('노트 삭제 실패:', deleteError)
      alert('삭제에 실패했습니다.')
    }
  }
}

// 태그 관련 함수들
const addTag = () => {
  const tag = newTag.value.trim().replace(/^#/, '').toLowerCase()
  if (tag && !note.value.tags.includes(tag)) {
    note.value.tags.push(tag)
    newTag.value = ''
    markAsChanged()
  }
}

const handleTagInput = (e) => {
  if (e.key === ',' || e.key === ' ') {
    e.preventDefault()
    addTag()
  }
}

const removeTag = (index) => {
  note.value.tags.splice(index, 1)
  markAsChanged()
}

// ✅ 간단한 자동저장 (eslint 에러 없음)
const markAsChanged = () => {
  // 🛡️ 저장 중이면 변경 감지 안함
  if (saving.value) {
    return
  }

  if (autoSave.value) {
    scheduleAutoSave()
  }
}

const scheduleAutoSave = () => {
  // 🚫 저장 중이면 스케줄 안함
  if (saving.value) {
    console.log('🚫 저장 중이므로 자동저장 스케줄 안함')
    return
  }

  // 🧹 기존 타이머들 완전 정리
  if (autoSaveTimeout.value) {
    clearTimeout(autoSaveTimeout.value)
    autoSaveTimeout.value = null
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }

  autoSavePending.value = false

  // ✅ 간단한 저장 조건 판단
  let shouldScheduleSave = false

  if (editorMode.value === 'new') {
    // 새 노트: 내용이 있어야 저장
    shouldScheduleSave = note.value.content && note.value.content.trim().length > 2
  } else if (editorMode.value === 'edit') {
    // 기존 노트: 변경사항이 있으면 저장
    shouldScheduleSave = hasUnsavedChanges.value
  }

  if (!shouldScheduleSave) {
    return
  }

  // ✅ 안전한 카운트다운 시작
  autoSavePending.value = true
  autoSaveCountdown.value = 3

  // 1초마다 카운트다운
  countdownInterval.value = setInterval(() => {
    autoSaveCountdown.value = Math.max(0, autoSaveCountdown.value - 1)

    // 0에 도달하면 interval 정리
    if (autoSaveCountdown.value <= 0) {
      clearInterval(countdownInterval.value)
      countdownInterval.value = null
    }
  }, 1000)

  // 3초 후 저장 실행
  autoSaveTimeout.value = setTimeout(async () => {
    // 🧹 정리
    autoSavePending.value = false
    if (countdownInterval.value) {
      clearInterval(countdownInterval.value)
      countdownInterval.value = null
    }

    // 저장 조건 재확인
    if (!hasUnsavedChanges.value || saving.value) {
      console.log('⏭️ 자동저장 건너뜀: 변경사항 없음 또는 저장 중')
      return
    }

    console.log('⏰ 자동저장 실행')
    await handleSave()
  }, 3000)
}

const handleContentChange = () => {
  markAsChanged()
}

const handleKeydown = (e) => {
  // Ctrl+S: 저장
  if (e.ctrlKey && e.key === 's') {
    e.preventDefault()
    handleSave()
  }

  // Ctrl+1,2,3: 뷰 모드 변경
  if (e.ctrlKey && e.key === '1') {
    e.preventDefault()
    setViewMode('edit')
  }
  if (e.ctrlKey && e.key === '2') {
    e.preventDefault()
    setViewMode('split')
  }
  if (e.ctrlKey && e.key === '3') {
    e.preventDefault()
    setViewMode('preview')
  }

  // Tab: 들여쓰기 (Edit 모드일 때만)
  if (e.key === 'Tab' && viewMode.value !== 'preview') {
    e.preventDefault()
    const start = e.target.selectionStart
    const end = e.target.selectionEnd
    const value = e.target.value

    e.target.value = value.substring(0, start) + '  ' + value.substring(end)
    e.target.selectionStart = e.target.selectionEnd = start + 2

    note.value.content = e.target.value
    markAsChanged()
  }
}

const focusContent = () => {
  nextTick(() => {
    contentTextarea.value?.focus()
  })
}

const setViewMode = (mode) => {
  viewMode.value = mode

  // 사용자 선호도 저장
  localStorage.setItem('noteEditor-viewMode', mode)

  // Preview Only 모드가 아닐 때는 에디터에 포커스
  if (mode !== 'preview') {
    nextTick(() => {
      if (mode === 'edit' && !note.value.title) {
        titleInput.value?.focus()
      } else {
        contentTextarea.value?.focus()
      }
    })
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const formatLastSaved = (date) => {
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)

  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

const getViewModeLabel = () => {
  switch (viewMode.value) {
    case 'edit': return '📝 Edit Mode'
    case 'split': return '🔄 Split View'
    case 'preview': return '👁️ Preview Mode'
    default: return 'Edit Mode'
  }
}

// ✅ 간단한 라우트 변경 감지
watch(() => route.params.id, async (newId, oldId) => {
  // 🛡️ 같은 ID면 무시
  if (newId === oldId) {
    return
  }

  console.log('🔄 라우트 변경 감지:', oldId, '→', newId)

  // 자동저장 타이머 취소
  if (autoSaveTimeout.value) {
    clearTimeout(autoSaveTimeout.value)
    autoSaveTimeout.value = null
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }
  autoSavePending.value = false

  if (hasUnsavedChanges.value) {
    const userChoice = confirm('저장하지 않은 변경사항이 있습니다. 저장하고 이동하시겠습니까?')

    if (userChoice) {
      await handleSave()
      await initializeEditor()
    } else {
      // 사용자가 저장하지 않기로 함
      await initializeEditor()
    }
  } else {
    await initializeEditor()
  }
}, { immediate: false })

// 라이프사이클
onMounted(async () => {
  await initializeEditor()

  // 저장된 뷰 모드 복원 (localStorage)
  const savedViewMode = localStorage.getItem('noteEditor-viewMode')
  if (savedViewMode && ['edit', 'split', 'preview'].includes(savedViewMode)) {
    viewMode.value = savedViewMode
  }

  // 페이지 떠날 때 저장 확인
  window.addEventListener('beforeunload', (e) => {
    if (hasUnsavedChanges.value) {
      e.preventDefault()
      e.returnValue = ''
    }
  })
})

onUnmounted(() => {
  console.log('🧹 NoteEditor 컴포넌트 정리 중...')

  // 🧹 모든 타이머 정리
  if (autoSaveTimeout.value) {
    clearTimeout(autoSaveTimeout.value)
    autoSaveTimeout.value = null
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }

  // 상태 리셋
  saving.value = false
  autoSavePending.value = false

  console.log('✅ NoteEditor 정리 완료')
})
</script>

<style scoped>
.prose {
  line-height: 1.7;
}

.prose h1, .prose h2, .prose h3 {
  color: #1f2937;
}

.prose h1 {
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.prose h2 {
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 0.25rem;
}

.prose p {
  margin-bottom: 1rem;
}

.prose ul, .prose ol {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

.prose code {
  background-color: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  color: #db2777;
}

.prose pre {
  background-color: #1f2937;
  color: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

.prose blockquote {
  border-left: 4px solid #3b82f6;
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
  color: #6b7280;
  background-color: #f8fafc;
  padding: 1rem;
  border-radius: 0.5rem;
}

.prose table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.prose th, .prose td {
  border: 1px solid #e5e7eb;
  padding: 0.5rem;
  text-align: left;
}

.prose th {
  background-color: #f9fafb;
  font-weight: 600;
}

/* 뷰 모드 토글 버튼 스타일 */
.view-mode-toggle {
  transition: all 0.2s ease;
}

.view-mode-toggle:hover {
  transform: translateY(-1px);
}
</style>
