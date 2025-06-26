<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <!-- 툴바 -->
    <div class="bg-white border-b border-gray-200 px-6 py-3">
      <div class="flex items-center justify-between">
        <!-- 왼쪽: 뒤로가기, 제목 -->
        <div class="flex items-center space-x-4 flex-1">
          <button
            @click="handleBack"
            class="text-gray-600 hover:text-blue-600 transition-colors"
          >
            ← 뒤로가기
          </button>

          <input
            ref="titleInput"
            v-model="note.title"
            @input="triggerAutoSave"
            placeholder="노트 제목..."
            class="text-xl font-semibold bg-transparent border-none outline-none text-gray-900 placeholder-gray-400 flex-1 min-w-0"
          />
        </div>

        <!-- 중앙: 뷰 모드 버튼들 -->
        <div class="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            @click="setViewMode('edit')"
            :class="{ 'bg-white shadow-sm': viewMode === 'edit' }"
            class="px-3 py-1 rounded text-sm font-medium transition-colors"
          >
            ✏️ 편집
          </button>
          <button
            @click="setViewMode('split')"
            :class="{ 'bg-white shadow-sm': viewMode === 'split' }"
            class="px-3 py-1 rounded text-sm font-medium transition-colors"
          >
            📱 분할
          </button>
          <button
            @click="setViewMode('preview')"
            :class="{ 'bg-white shadow-sm': viewMode === 'preview' }"
            class="px-3 py-1 rounded text-sm font-medium transition-colors"
          >
            👁️ 미리보기
          </button>
        </div>

        <!-- 우측: 액션 버튼들 -->
        <div class="flex items-center space-x-3">
          <button
            v-if="editorMode === 'edit'"
            @click="handleDelete"
            class="text-red-600 hover:text-red-700 transition-colors"
          >
            🗑️ 삭제
          </button>

          <button
            @click="handleSave"
            :disabled="saving"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
          >
            <span v-if="saving">💾</span>
            <span v-else>💾</span>
            <span>{{ saving ? '저장 중...' : '저장' }}</span>
          </button>
        </div>
      </div>

      <!-- 태그 관리 -->
      <div class="mt-3 flex items-center space-x-4">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-sm text-gray-600">태그:</span>
          <span
            v-for="tag in note.tags"
            :key="tag"
            class="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium group cursor-pointer"
            @click="removeTag(tag)"
          >
            {{ tag }}
            <span class="ml-1 opacity-0 group-hover:opacity-100 transition-opacity">✕</span>
          </span>
          <input
            v-model="newTag"
            @keydown="handleTagInput"
            placeholder="새 태그 추가..."
            class="text-xs bg-transparent border border-gray-300 rounded-full px-2 py-1 min-w-0 w-24 focus:w-32 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>

    <!-- 메인 에디터 영역 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 좌측 패널 (편집기) -->
      <div
        :class="{
          'w-full': viewMode === 'edit' || viewMode === 'preview',
          'w-1/2': viewMode === 'split'
        }"
        class="flex flex-col border-r border-gray-200"
      >
        <!-- Split 모드에서 우측 패널 선택 -->
        <div
          v-if="viewMode === 'split'"
          class="bg-gray-50 border-b border-gray-200 px-4 py-2"
        >
          <div class="flex items-center justify-between">
            <div class="flex space-x-2">
              <button
                @click="setSplitPanel('preview')"
                :class="{ 'bg-white shadow-sm text-blue-600': splitPanel === 'preview' }"
                class="px-3 py-1 rounded text-sm font-medium transition-colors"
              >
                👁️ 미리보기
              </button>
              <button
                @click="setSplitPanel('ai-chat')"
                :class="{ 'bg-white shadow-sm text-blue-600': splitPanel === 'ai-chat' }"
                class="px-3 py-1 rounded text-sm font-medium transition-colors"
              >
                🤖 AI 채팅
              </button>
            </div>

            <div class="flex items-center space-x-4 text-xs text-gray-500">
              <span>{{ wordCount }}단어, {{ characterCount }}글자</span>
              <span v-if="lastSaved" class="text-green-600">
                저장됨: {{ formatTime(lastSaved) }}
              </span>
              <button
                @click="toggleAutoSave"
                :class="autoSave ? 'text-green-600' : 'text-gray-400'"
                class="hover:text-blue-600 transition-colors"
              >
                자동저장: {{ autoSave ? '켜짐' : '꺼짐' }}
              </button>
              <span class="text-gray-400">Ctrl+1,2,3: 뷰 모드</span>
            </div>
          </div>
        </div>

        <!-- 노트 내용 에디터 -->
        <div class="flex-1 p-6">
          <textarea
            ref="contentTextarea"
            v-model="note.content"
            @input="triggerAutoSave"
            placeholder="노트 작성을 시작하세요..."
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
              미리보기
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
            {{ note.title || '제목 없음' }}
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
              생성: {{ formatDate(note.created_at) }}
            </div>
            <div v-if="note.updated_at && note.updated_at !== note.created_at">
              수정: {{ formatDate(note.updated_at) }}
            </div>
            <div>{{ wordCount }}단어, {{ characterCount}}글자</div>
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
import AIChatPanel from '../components/AIChatPanel.vue'

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
const splitPanel = ref('preview') // 'preview', 'ai-chat'
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
  if (!note.value.content) return '<p class="text-gray-400">작성을 시작하면 미리보기가 표시됩니다...</p>'

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

// 뷰 모드 설정
const setViewMode = (mode) => {
  viewMode.value = mode
  localStorage.setItem('noteEditor-viewMode', mode)
}

// Split 패널 설정
const setSplitPanel = (panel) => {
  splitPanel.value = panel
  localStorage.setItem('noteEditor-splitPanel', panel)
}

// AI 콘텐츠 삽입
const insertAIContentToNote = (content) => {
  const textarea = contentTextarea.value
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const currentContent = note.value.content

    const newContent = currentContent.substring(0, start) +
                      '\n\n' + content + '\n\n' +
                      currentContent.substring(end)

    note.value.content = newContent
    triggerAutoSave()

    nextTick(() => {
      textarea.focus()
      const newCursorPos = start + content.length + 4
      textarea.setSelectionRange(newCursorPos, newCursorPos)
    })
  }
}

// 태그 관련
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

// 자동저장 관련
const toggleAutoSave = () => {
  autoSave.value = !autoSave.value
  localStorage.setItem('noteEditor-autoSave', autoSave.value.toString())

  if (!autoSave.value) {
    clearAutoSaveTimer()
  }
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

const triggerAutoSave = () => {
  if (!autoSave.value) return
  if (editorMode.value === 'unknown') return

  clearAutoSaveTimer()
  autoSavePending.value = true
  autoSaveCountdown.value = 3

  // 카운트다운 시작
  countdownInterval.value = setInterval(() => {
    autoSaveCountdown.value--
    if (autoSaveCountdown.value <= 0) {
      clearInterval(countdownInterval.value)
      performAutoSave()
    }
  }, 1000)
}

const performAutoSave = async () => {
  if (!hasUnsavedChanges.value) {
    autoSavePending.value = false
    return
  }

  try {
    console.log('🔄 자동저장 시작')

    let savedNote
    if (editorMode.value === 'new') {
      savedNote = await notesStore.createNote(note.value)
      editorMode.value = 'edit'
      currentNoteId.value = savedNote.id
      await router.replace(`/notes/${savedNote.id}`)
    } else {
      savedNote = await notesStore.updateNote(currentNoteId.value, note.value)
    }

    originalNote.value = JSON.parse(JSON.stringify(savedNote))
    lastSaved.value = new Date()

    console.log('✅ 자동저장 완료')

  } catch (error) {
    console.error('❌ 자동저장 실패:', error)
  } finally {
    autoSavePending.value = false
  }
}

// 저장 관련
const handleSave = async () => {
  if (saving.value) return

  saving.value = true
  clearAutoSaveTimer()

  try {
    let savedNote
    if (editorMode.value === 'new') {
      savedNote = await notesStore.createNote(note.value)
      editorMode.value = 'edit'
      currentNoteId.value = savedNote.id
      await router.replace(`/notes/${savedNote.id}`)
    } else {
      savedNote = await notesStore.updateNote(currentNoteId.value, note.value)
    }

    originalNote.value = JSON.parse(JSON.stringify(savedNote))
    lastSaved.value = new Date()

  } catch (error) {
    console.error('저장 실패:', error)
    alert('저장에 실패했습니다.')
  } finally {
    saving.value = false
  }
}

// 뒤로가기
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

// 삭제
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

// 유틸리티 함수
const formatTime = (date) => {
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// 에디터 초기화
const initializeEditor = async () => {
  const routeId = route.params.id

  if (!routeId || routeId === 'new') {
    editorMode.value = 'new'
    note.value = {
      id: null,
      title: '제목 없음',
      content: '',
      tags: []
    }
    originalNote.value = JSON.parse(JSON.stringify(note.value))

    nextTick(() => {
      titleInput.value?.focus()
      titleInput.value?.select()
    })
  } else {
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
})
</script>

<style scoped>
.prose {
  max-width: none;
}

.prose h1, .prose h2, .prose h3 {
  color: #374151;
}

.prose code {
  color: #6366f1;
  background-color: #f3f4f6;
}

.prose strong {
  color: #111827;
}
</style>
