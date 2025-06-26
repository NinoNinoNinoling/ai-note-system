<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <!-- 상단 헤더 -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button
            @click="handleBack"
            class="text-gray-600 hover:text-gray-900 transition-colors"
            title="Go back to notes list"
          >
            ← Back
          </button>

          <h1 class="text-xl font-semibold text-gray-900">
            {{ editorMode === 'new' ? 'New Note' : 'Edit Note' }}
          </h1>
        </div>

        <!-- 뷰 모드 토글 -->
        <div class="flex items-center space-x-4">
          <div class="flex bg-gray-100 rounded-lg p-1">
            <button
              @click="setViewMode('edit')"
              :class="[
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors view-mode-toggle',
                viewMode === 'edit'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
              title="Edit Mode (Ctrl+1)"
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

          <!-- Split 모드일 때 우측 패널 선택 -->
          <div v-if="viewMode === 'split'" class="flex bg-gray-100 rounded-lg p-1">
            <button
              @click="setSplitPanel('preview')"
              :class="[
                'px-2 py-1 rounded text-xs font-medium transition-colors',
                splitPanel === 'preview'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              👁️ Preview
            </button>
            <button
              @click="setSplitPanel('ai-chat')"
              :class="[
                'px-2 py-1 rounded text-xs font-medium transition-colors',
                splitPanel === 'ai-chat'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              🤖 AI Chat
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
        <!-- 노트 제목 -->
        <div class="p-6 border-b border-gray-100">
          <input
            ref="titleInput"
            v-model="note.title"
            @input="triggerAutoSave"
            type="text"
            placeholder="Enter note title..."
            class="w-full text-2xl font-bold text-gray-900 placeholder-gray-400 border-none outline-none bg-transparent"
          />
        </div>

        <!-- 태그 입력 영역 -->
        <div class="px-6 py-3 border-b border-gray-100 bg-gray-50">
          <div class="flex flex-wrap items-center gap-2">
            <!-- 기존 태그들 -->
            <div
              v-for="tag in note.tags"
              :key="tag"
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              {{ tag }}
              <button
                @click="removeTag(tag)"
                class="ml-1.5 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </div>

            <!-- 새 태그 입력 -->
            <input
              v-model="newTag"
              @keydown="handleTagInput"
              type="text"
              placeholder="Add tag..."
              class="flex-shrink-0 px-3 py-1 text-xs border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <!-- 에디터 도구 모음 -->
        <div class="px-6 py-2 border-b border-gray-100 bg-gray-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4 text-sm text-gray-600">
              <span>{{ wordCount }} words</span>
              <span>{{ characterCount }} characters</span>
            </div>

            <div class="flex items-center space-x-4 text-sm">
              <button
                @click="toggleAutoSave"
                :class="autoSave ? 'text-green-600' : 'text-gray-400'"
                class="hover:text-blue-600 transition-colors"
              >
                Auto-save: {{ autoSave ? 'On' : 'Off' }}
              </button>
              <span class="text-gray-400">Ctrl+1,2,3: View modes</span>
            </div>
          </div>
        </div>

        <!-- 노트 내용 에디터 -->
        <div class="flex-1 p-6">
          <textarea
            ref="contentTextarea"
            v-model="note.content"
            @input="triggerAutoSave"
            placeholder="Start writing your note..."
            class="w-full h-full resize-none border-none outline-none text-gray-900 placeholder-gray-400 leading-relaxed"
          ></textarea>
        </div>
      </div>

      <!-- 우측 패널 (Split 모드에서만 표시) -->
      <div
        v-if="viewMode === 'split'"
        class="w-1/2 flex flex-col"
      >
        <!-- Preview 패널 -->
        <div
          v-if="splitPanel === 'preview'"
          class="h-full bg-white overflow-y-auto"
        >
          <div class="p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4 border-b pb-2">
              Preview
            </h2>
            <div
              class="prose max-w-none"
              v-html="renderedContent"
            ></div>
          </div>
        </div>

        <!-- AI Chat 패널 -->
        <AIChatPanel
          v-else-if="splitPanel === 'ai-chat'"
          :note-content="note.content"
          @insert-to-note="insertAIContentToNote"
        />
      </div>

      <!-- Preview Only 모드 -->
      <div
        v-if="viewMode === 'preview'"
        class="w-full bg-white overflow-y-auto"
      >
        <div class="max-w-4xl mx-auto p-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-8">
            {{ note.title || 'Untitled' }}
          </h1>

          <!-- 태그들 -->
          <div v-if="note.tags && note.tags.length > 0" class="mb-6">
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in note.tags"
                :key="tag"
                class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- 메타데이터 -->
          <div class="mb-8 text-sm text-gray-500 border-b pb-4">
            <div v-if="note.created_at" class="mb-1">
              Created: {{ formatDate(note.created_at) }}
            </div>
            <div v-if="note.updated_at && note.updated_at !== note.created_at">
              Updated: {{ formatDate(note.updated_at) }}
            </div>
            <div>{{ wordCount }} words, {{ characterCount }} characters</div>
          </div>

          <!-- 렌더링된 내용 -->
          <div
            class="prose prose-lg max-w-none"
            v-html="renderedContent"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNotesStore } from '../stores/notes'
import AIChatPanel from '../components/AIChatPanel.vue' // AI 채팅 패널 컴포넌트

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
const viewMode = ref('edit') // 'edit', 'split', 'preview'
const splitPanel = ref('preview') // 'preview', 'ai-chat' (split 모드에서 우측 패널)
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

// AI 채팅 관련 메서드
const setSplitPanel = (panel) => {
  splitPanel.value = panel
  localStorage.setItem('noteEditor-splitPanel', panel)
}

const insertAIContentToNote = (content) => {
  // AI 응답을 노트 내용에 삽입
  const textarea = contentTextarea.value
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const currentContent = note.value.content

    // 커서 위치 또는 선택된 텍스트를 AI 내용으로 교체
    const newContent = currentContent.substring(0, start) +
                      '\n\n' + content + '\n\n' +
                      currentContent.substring(end)

    note.value.content = newContent
    triggerAutoSave()

    // 포커스를 에디터로 돌리고 커서 위치 조정
    nextTick(() => {
      textarea.focus()
      const newCursorPos = start + content.length + 4 // 4는 \n\n의 길이
      textarea.setSelectionRange(newCursorPos, newCursorPos)
    })
  }
}

// 기존 메서드들은 동일하게 유지...
// (여기서는 생략하고 핵심 AI 기능만 표시)

// 태그 관련 메서드
const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !note.value.tags.includes(tag)) {
    note.value.tags.push(tag)
    newTag.value = ''
    triggerAutoSave()
  }
}

const removeTag = (tagToRemove) => {
  note.value.tags = note.value.tags.filter(tag => tag !== tagToRemove)
  triggerAutoSave()
}

const handleTagInput = (e) => {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addTag()
  }
}

// 저장 관련 메서드들
const handleSave = async () => {
  if (saving.value) return

  console.log('💾 수동 저장 시작')
  saving.value = true

  try {
    let savedNote
    if (editorMode.value === 'new') {
      savedNote = await notesStore.createNote(note.value)
      // 새 노트 생성 후 편집 모드로 전환
      editorMode.value = 'edit'
      currentNoteId.value = savedNote.id
      await router.replace(`/notes/${savedNote.id}`)
    } else {
      savedNote = await notesStore.updateNote(currentNoteId.value, note.value)
    }

    originalNote.value = JSON.parse(JSON.stringify(savedNote))
    lastSaved.value = new Date()

    // 자동저장 타이머 취소
    clearAutoSaveTimer()

    console.log('✅ 수동 저장 완료')

  } catch (error) {
    console.error('💥 저장 실패:', error)
    alert('저장에 실패했습니다.')
  } finally {
    saving.value = false
  }
}

const triggerAutoSave = () => {
  if (!autoSave.value) return

  clearAutoSaveTimer()

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

  // 3초 후 자동 저장
  autoSaveTimeout.value = setTimeout(() => {
    performAutoSave()
  }, 3000)
}

const performAutoSave = async () => {
  if (!hasUnsavedChanges.value || saving.value) {
    autoSavePending.value = false
    return
  }

  console.log('🔄 자동 저장 실행')
  autoSavePending.value = false

  // 필수 필드 검증
  if (!note.value.title.trim()) {
    console.log('⚠️ 자동 저장 취소: 제목이 비어있음')
    return
  }

  await handleSave()
}

const clearAutoSaveTimer = () => {
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

const toggleAutoSave = () => {
  autoSave.value = !autoSave.value
  localStorage.setItem('noteEditor-autoSave', autoSave.value.toString())

  if (!autoSave.value) {
    clearAutoSaveTimer()
  }

  console.log(`🔄 자동저장 ${autoSave.value ? '활성화' : '비활성화'}`)
}

// 뷰 모드 함수들
const setViewMode = (mode) => {
  viewMode.value = mode
  localStorage.setItem('noteEditor-viewMode', mode)

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

// 기타 유틸리티 함수들
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

const handleBack = () => {
  if (hasUnsavedChanges.value) {
    const shouldSave = confirm('저장하지 않은 변경사항이 있습니다. 저장하고 나가시겠습니까?')
    if (shouldSave) {
      handleSave().then(() => {
        router.push('/notes')
      })
      return
    }
  }
  router.push('/notes')
}

const handleDelete = async () => {
  if (editorMode.value !== 'edit') return

  const confirmed = confirm('정말로 이 노트를 삭제하시겠습니까?')
  if (!confirmed) return

  try {
    await notesStore.deleteNote(currentNoteId.value)
    router.push('/notes')
  } catch (error) {
    console.error('삭제 실패:', error)
    alert('노트 삭제에 실패했습니다.')
  }
}

// 에디터 초기화 (간소화)
const initializeEditor = async () => {
  console.log('🚀 에디터 초기화 중...')

  const routeId = route.params.id

  if (!routeId || routeId === 'new') {
    // 새 노트
    editorMode.value = 'new'
    note.value = {
      id: null,
      title: 'Untitled',
      content: '',
      tags: []
    }
    originalNote.value = JSON.parse(JSON.stringify(note.value))

    nextTick(() => {
      titleInput.value?.focus()
      titleInput.value?.select()
    })
  } else {
    // 기존 노트 편집
    editorMode.value = 'edit'
    currentNoteId.value = parseInt(routeId)

    try {
      const loadedNote = await notesStore.fetchNote(currentNoteId.value)
      note.value = { ...loadedNote }
      originalNote.value = JSON.parse(JSON.stringify(loadedNote))
    } catch (error) {
      console.error('노트 로드 실패:', error)
      alert('노트를 불러올 수 없습니다.')
      router.push('/notes')
    }
  }
}

// 라이프사이클
onMounted(async () => {
  await initializeEditor()

  // 저장된 설정 복원
  const savedViewMode = localStorage.getItem('noteEditor-viewMode')
  if (savedViewMode && ['edit', 'split', 'preview'].includes(savedViewMode)) {
    viewMode.value = savedViewMode
  }

  const savedSplitPanel = localStorage.getItem('noteEditor-splitPanel')
  if (savedSplitPanel && ['preview', 'ai-chat'].includes(savedSplitPanel)) {
    splitPanel.value = savedSplitPanel
  }

  const savedAutoSave = localStorage.getItem('noteEditor-autoSave')
  if (savedAutoSave !== null) {
    autoSave.value = savedAutoSave === 'true'
  }

  window.addEventListener('keydown', handleKeyboard)

  window.addEventListener('beforeunload', (e) => {
    if (hasUnsavedChanges.value) {
      e.preventDefault()
      e.returnValue = ''
    }
  })
})

onUnmounted(() => {
  clearAutoSaveTimer()
  window.removeEventListener('keydown', handleKeyboard)
})

// 라우트 변경 감지
watch(() => route.params.id, async (newId, oldId) => {
  if (newId === oldId) return

  clearAutoSaveTimer()

  if (hasUnsavedChanges.value) {
    const userChoice = confirm('저장하지 않은 변경사항이 있습니다. 저장하고 이동하시겠습니까?')
    if (userChoice) {
      await handleSave()
    }
  }

  await initializeEditor()
}, { immediate: false })
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

.view-mode-toggle {
  transition: all 0.2s ease;
}

.view-mode-toggle:hover {
  transform: translateY(-1px);
}
</style>
