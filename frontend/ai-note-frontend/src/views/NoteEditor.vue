<template>
  <div class="h-full flex flex-col bg-gray-50">
    <!-- 상단 헤더 -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <!-- 뒤로가기 및 제목 -->
        <div class="flex items-center space-x-4">
          <button
            @click="handleBack"
            class="text-gray-600 hover:text-gray-900 transition-colors"
            title="Back to Notes"
          >
            ← Back
          </button>
          <h1 class="text-xl font-semibold text-gray-900">
            {{ editorMode === 'new' ? '📝 New Note' : '✏️ Edit Note' }}
          </h1>
        </div>

        <!-- 뷰 모드 토글 -->
        <div class="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
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
          viewMode === 'split' ? 'w-1/2' : 'w-full'
        ]"
      >
        <div class="p-6 flex-1 flex flex-col space-y-4">
          <!-- 제목 입력 -->
          <div>
            <input
              ref="titleInput"
              v-model="note.title"
              type="text"
              placeholder="Enter note title..."
              class="w-full text-2xl font-bold text-gray-900 placeholder-gray-400 border-none outline-none resize-none bg-transparent"
              @input="handleContentChange"
            />
          </div>

          <!-- 태그 입력 -->
          <div class="flex flex-wrap items-center gap-2">
            <span
              v-for="tag in note.tags"
              :key="tag"
              class="inline-flex items-center px-2.5 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
            >
              #{{ tag }}
              <button
                @click="removeTag(tag)"
                class="ml-1 text-blue-600 hover:text-red-600 transition-colors"
              >
                ×
              </button>
            </span>
            <div class="flex items-center space-x-2">
              <input
                v-model="newTag"
                type="text"
                placeholder="Add tag..."
                class="px-2 py-1 border border-gray-300 rounded text-sm"
                @keydown.enter="addTag"
                @keydown.space="addTag"
              />
              <button
                @click="addTag"
                class="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                + Add
              </button>
            </div>
          </div>

          <!-- 내용 입력 -->
          <div class="flex-1">
            <textarea
              ref="contentTextarea"
              v-model="note.content"
              placeholder="Start writing your note..."
              class="w-full h-full text-gray-900 placeholder-gray-400 border-none outline-none resize-none bg-transparent font-mono leading-relaxed"
              @input="handleContentChange"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- 미리보기 패널 -->
      <div
        v-if="viewMode === 'preview' || viewMode === 'split'"
        :class="[
          'bg-gray-50 border-l border-gray-200 overflow-y-auto',
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
// ✅ showPreview 변수 제거 (ESLint 오류 해결)
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

// 에디터 초기화
const initializeEditor = async () => {
  console.log('🚀 에디터 초기화 중...')

  if (!determineEditorMode()) {
    alert('올바르지 않은 노트 경로입니다.')
    router.push('/notes')
    return
  }

  console.log(`📝 에디터 모드: ${editorMode.value}`)

  if (editorMode.value === 'new') {
    initializeNewNote()
  } else if (editorMode.value === 'edit') {
    await loadExistingNote()
  }
}

// 태그 관리
const addTag = () => {
  const tag = newTag.value.trim().replace(/^#/, '')
  if (tag && !note.value.tags.includes(tag)) {
    note.value.tags.push(tag)
    newTag.value = ''
    handleContentChange()
  }
}

const removeTag = (tagToRemove) => {
  note.value.tags = note.value.tags.filter(tag => tag !== tagToRemove)
  handleContentChange()
}

// 내용 변경 처리
const handleContentChange = () => {
  if (autoSave.value && !autoSavePending.value) {
    scheduleAutoSave()
  }
}

// 자동저장 스케줄링
const scheduleAutoSave = () => {
  // 기존 타이머 취소
  if (autoSaveTimeout.value) {
    clearTimeout(autoSaveTimeout.value)
    autoSaveTimeout.value = null
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }

  autoSavePending.value = true
  autoSaveCountdown.value = 3

  // 카운트다운 시작
  countdownInterval.value = setInterval(() => {
    autoSaveCountdown.value--
    if (autoSaveCountdown.value <= 0) {
      clearInterval(countdownInterval.value)
      countdownInterval.value = null
    }
  }, 1000)

  // 3초 후 자동저장
  autoSaveTimeout.value = setTimeout(async () => {
    try {
      await handleSave(true) // 자동저장 플래그
    } catch (autoSaveError) {
      console.error('자동저장 실패:', autoSaveError)
    } finally {
      autoSavePending.value = false
      autoSaveTimeout.value = null
    }
  }, 3000)
}

// 저장 처리
const handleSave = async (isAutoSave = false) => {
  if (saving.value) return

  try {
    saving.value = true

    if (!isAutoSave) {
      // 수동 저장 시 자동저장 타이머 취소
      if (autoSaveTimeout.value) {
        clearTimeout(autoSaveTimeout.value)
        autoSaveTimeout.value = null
      }
      if (countdownInterval.value) {
        clearInterval(countdownInterval.value)
        countdownInterval.value = null
      }
      autoSavePending.value = false
    }

    let savedNote
    if (editorMode.value === 'new') {
      savedNote = await notesStore.createNote(note.value)
      console.log('✅ 새 노트 생성 완료:', savedNote.id)

      // 새 노트 생성 후 편집 모드로 전환
      editorMode.value = 'edit'
      currentNoteId.value = savedNote.id

      // URL 업데이트 (히스토리 추가 없이)
      router.replace(`/notes/${savedNote.id}`)
    } else {
      savedNote = await notesStore.updateNote(currentNoteId.value, note.value)
      console.log('✅ 노트 수정 완료:', savedNote.id)
    }

    // 저장된 노트로 상태 업데이트
    note.value = { ...savedNote }
    originalNote.value = JSON.parse(JSON.stringify(savedNote))
    lastSaved.value = new Date()

    if (!isAutoSave) {
      console.log('💾 수동 저장 완료')
    }

  } catch (saveError) {
    console.error('❌ 저장 실패:', saveError)
    alert(`저장에 실패했습니다: ${saveError.message}`)
  } finally {
    saving.value = false
  }
}

// 삭제 처리
const handleDelete = async () => {
  if (editorMode.value !== 'edit' || !currentNoteId.value) return

  const confirmDelete = confirm(`정말로 노트 "${note.value.title}"를 삭제하시겠습니까?`)
  if (!confirmDelete) return

  try {
    await notesStore.deleteNote(currentNoteId.value)
    console.log('✅ 노트 삭제 완료')
    router.push('/notes')
  } catch (deleteError) {
    console.error('❌ 삭제 실패:', deleteError)
    alert(`삭제에 실패했습니다: ${deleteError.message}`)
  }
}

// 뒤로가기
const handleBack = async () => {
  if (hasUnsavedChanges.value) {
    const userChoice = confirm('저장하지 않은 변경사항이 있습니다. 저장하고 이동하시겠습니까?')
    if (userChoice) {
      await handleSave()
    }
  }
  router.push('/notes')
}

// 키보드 단축키
const handleKeyboard = (e) => {
  if (e.ctrlKey || e.metaKey) {
    if (e.key === 's') {
      e.preventDefault()
      handleSave()
    } else if (e.key === '1') {
      e.preventDefault()
      setViewMode('edit')
    } else if (e.key === '2') {
      e.preventDefault()
      setViewMode('split')
    } else if (e.key === '3') {
      e.preventDefault()
      setViewMode('preview')
    }
  }
}

// 뷰 모드 함수들
// eslint-disable-next-line no-unused-vars
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

  // 키보드 이벤트 리스너
  window.addEventListener('keydown', handleKeyboard)

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

  // 이벤트 리스너 제거
  window.removeEventListener('keydown', handleKeyboard)

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
