<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <!-- 헤더 -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-600 rounded-lg flex items-center justify-center">
            <span class="text-white text-sm font-bold">🧠</span>
          </div>
          <div>
            <h1 class="text-xl font-semibold text-gray-900">지식 어시스턴트</h1>
            <p class="text-sm text-gray-500">{{ totalNotes }}개 노트를 기반으로 한 지능형 검색 및 분석</p>
          </div>
        </div>

        <!-- 컨트롤 패널 -->
        <div class="flex items-center space-x-4">
          <!-- 노트 상태 표시 -->
          <div class="flex items-center space-x-2 text-sm text-gray-600">
            <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>{{ totalNotes }}개 노트</span>
            <span>•</span>
            <span>{{ totalWords }}단어</span>
          </div>

          <!-- 액션 버튼들 -->
          <button
            @click="refreshNotes"
            :disabled="isRefreshing"
            class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ isRefreshing ? '🔄 새로고침 중...' : '🔄 새로고침' }}
          </button>

          <button
            @click="clearHistory"
            class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            🗑️ 대화 초기화
          </button>
        </div>
      </div>
    </div>

    <!-- 메인 채팅 영역 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 채팅 메시지 영역 -->
      <div class="flex-1 flex flex-col">
        <div
          ref="chatContainer"
          class="flex-1 overflow-y-auto p-6 space-y-6"
        >
          <!-- 시작 메시지 -->
          <div v-if="messages.length === 0" class="text-center py-12">
            <div class="w-20 h-20 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full mx-auto mb-6 flex items-center justify-center">
              <span class="text-white text-3xl">🧠</span>
            </div>
            <h3 class="text-2xl font-semibold text-gray-900 mb-3">노트 지식 어시스턴트</h3>
            <p class="text-gray-600 mb-8 max-w-lg mx-auto">
              전체 {{ totalNotes }}개 노트를 기반으로 질문에 답변하고, 지식을 분석하며, 연결점을 찾아드립니다.
            </p>

            <!-- 추천 질문들 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
              <!-- 지식 질문 -->
              <div class="space-y-3">
                <h4 class="text-sm font-medium text-gray-700">💡 지식 탐색 질문</h4>
                <div class="space-y-2">
                  <button
                    v-for="question in knowledgeQuestions"
                    :key="question"
                    @click="sendQuickMessage(question)"
                    class="w-full text-left p-3 text-sm text-gray-700 bg-white hover:bg-blue-50 hover:text-blue-700 rounded-lg border border-gray-200 hover:border-blue-300 transition-all"
                  >
                    {{ question }}
                  </button>
                </div>
              </div>

              <!-- 분석 질문 -->
              <div class="space-y-3">
                <h4 class="text-sm font-medium text-gray-700">📊 분석 질문</h4>
                <div class="space-y-2">
                  <button
                    v-for="question in analysisQuestions"
                    :key="question"
                    @click="sendQuickMessage(question)"
                    class="w-full text-left p-3 text-sm text-gray-700 bg-white hover:bg-green-50 hover:text-green-700 rounded-lg border border-gray-200 hover:border-green-300 transition-all"
                  >
                    {{ question }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 채팅 메시지들 -->
          <div v-for="(message, index) in messages" :key="index" class="flex">
            <!-- 사용자 메시지 -->
            <div v-if="message.type === 'user'" class="flex justify-end w-full">
              <div class="max-w-2xl">
                <div class="bg-blue-600 text-white rounded-2xl rounded-br-md px-6 py-4">
                  <p class="text-sm leading-relaxed">{{ message.content }}</p>
                </div>
                <div class="text-xs text-gray-500 mt-1 text-right">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>

            <!-- AI 메시지 -->
            <div v-else class="flex justify-start w-full">
              <div class="max-w-4xl">
                <div class="flex items-start space-x-3">
                  <div class="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-600 rounded-lg flex items-center justify-center mt-1">
                    <span class="text-white text-xs font-bold">🧠</span>
                  </div>

                  <div class="flex-1">
                    <div class="bg-white rounded-2xl rounded-bl-md px-6 py-4 shadow-sm border border-gray-100">
                      <!-- 로딩 상태 -->
                      <div v-if="message.isLoading" class="flex items-center space-x-3 text-purple-600">
                        <div class="animate-spin rounded-full h-4 w-4 border-2 border-purple-300 border-t-purple-600"></div>
                        <span class="text-sm text-gray-500">노트들을 분석하고 있습니다...</span>
                      </div>

                      <!-- AI 응답 내용 -->
                      <div v-else>
                        <div
                          class="prose max-w-none text-sm leading-relaxed"
                          v-html="formatMessage(message.content)"
                        ></div>

                        <!-- 관련 노트들 표시 -->
                        <div v-if="message.relatedNotes && message.relatedNotes.length > 0" class="mt-4 pt-3 border-t border-gray-100">
                          <div class="text-xs text-gray-500 mb-2">📝 관련 노트</div>
                          <div class="flex flex-wrap gap-2">
                            <button
                              v-for="note in message.relatedNotes.slice(0, 3)"
                              :key="note.id"
                              @click="openNote(note.id)"
                              class="inline-flex items-center px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-xs hover:bg-purple-100 transition-colors"
                            >
                              📄 {{ note.title }}
                            </button>
                          </div>
                        </div>
                      </div>

                      <!-- 액션 버튼들 -->
                      <div v-if="message.content && !message.isLoading" class="flex space-x-2 mt-3">
                        <button
                          @click="copyMessage(message.content)"
                          class="text-xs px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                        >
                          📋 복사
                        </button>
                        <button
                          @click="continueConversation(message.content)"
                          class="text-xs px-3 py-1.5 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                        >
                          💭 더 자세히
                        </button>
                        <button
                          @click="findRelatedNotes(message.content)"
                          class="text-xs px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                        >
                          🔗 관련 노트
                        </button>
                      </div>
                    </div>

                    <div class="text-xs text-gray-500 mt-1">
                      {{ formatTime(message.timestamp) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 입력 영역 -->
        <div class="bg-white border-t border-gray-200 p-6">
          <div class="max-w-4xl mx-auto">
            <div class="relative">
              <textarea
                ref="messageInput"
                v-model="currentMessage"
                @keydown="handleKeydown"
                @input="adjustTextareaHeight"
                :disabled="isLoading"
                placeholder="전체 노트에 대해 질문해보세요... (예: '프로젝트 관련 노트들 요약해줘', 'AI에 대해 뭘 공부했는지 알려줘')"
                class="w-full px-6 py-4 pr-16 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500 text-base"
                rows="1"
              ></textarea>

              <button
                @click="sendMessage"
                :disabled="!currentMessage.trim() || isLoading"
                :class="[
                  'absolute right-3 top-1/2 transform -translate-y-1/2 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200',
                  currentMessage.trim() && !isLoading
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 shadow-lg'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                ]"
              >
                <svg v-if="!isLoading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
                <div v-else class="w-5 h-5">
                  <div class="w-5 h-5 border-2 border-gray-400 border-t-white rounded-full animate-spin"></div>
                </div>
              </button>
            </div>

            <!-- 입력 힌트 -->
            <div class="flex items-center justify-between mt-3 text-sm text-gray-500">
              <span>🧠 {{ totalNotes }}개 노트의 지식을 활용해 답변합니다</span>
              <span>Enter로 전송, Shift+Enter로 줄바꿈</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 우측 사이드바 -->
      <div class="w-80 bg-white border-l border-gray-200 flex flex-col">
        <!-- 사이드바 헤더 -->
        <div class="p-4 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">📊 노트 현황</h3>
        </div>

        <!-- 노트 통계 -->
        <div class="p-4 space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div class="text-center p-3 bg-purple-50 rounded-lg">
              <div class="text-lg font-bold text-purple-700">{{ totalNotes }}</div>
              <div class="text-xs text-purple-600">총 노트</div>
            </div>
            <div class="text-center p-3 bg-blue-50 rounded-lg">
              <div class="text-lg font-bold text-blue-700">{{ totalWords }}</div>
              <div class="text-xs text-blue-600">총 단어</div>
            </div>
          </div>

          <!-- 최근 노트들 -->
          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-2">📝 최근 노트</h4>
            <div class="space-y-2">
              <button
                v-for="note in recentNotes.slice(0, 5)"
                :key="note.id"
                @click="openNote(note.id)"
                class="w-full text-left p-2 text-xs text-gray-700 hover:bg-gray-50 rounded border border-gray-100 hover:border-gray-200 transition-colors"
              >
                <div class="font-medium truncate">{{ note.title }}</div>
                <div class="text-gray-500 mt-1">{{ formatDate(note.updated_at) }}</div>
              </button>
            </div>
          </div>

          <!-- 인기 태그들 -->
          <div v-if="popularTags.length > 0">
            <h4 class="text-sm font-medium text-gray-700 mb-2">🏷️ 인기 태그</h4>
            <div class="flex flex-wrap gap-1">
              <button
                v-for="tag in popularTags.slice(0, 8)"
                :key="tag"
                @click="searchByTag(tag)"
                class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                #{{ tag }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useNotesStore } from '../stores/notes'

const router = useRouter()
const notesStore = useNotesStore()

// 템플릿 참조
const chatContainer = ref(null)
const messageInput = ref(null)

// 상태
const messages = ref([])
const currentMessage = ref('')
const isLoading = ref(false)
const isRefreshing = ref(false)
const notes = ref([])

// 추천 질문들
const knowledgeQuestions = [
  "내 노트들에서 가장 많이 다룬 주제는 뭐야?",
  "최근에 작성한 노트들을 요약해줘",
  "AI나 기술 관련 노트들을 찾아줘",
  "프로젝트 관련 내용들을 정리해줘"
]

const analysisQuestions = [
  "노트들 사이의 연관성을 분석해줘",
  "부족한 지식 영역을 찾아줘",
  "학습 패턴을 분석해줘",
  "다음에 공부하면 좋을 주제 추천해줘"
]

// 컴퓨티드
const totalNotes = computed(() => notes.value.length)

const totalWords = computed(() => {
  return notes.value.reduce((total, note) => {
    const wordCount = note.content ?
      note.content.split(/\s+/).filter(word => word.length > 0).length : 0
    return total + wordCount
  }, 0)
})

const recentNotes = computed(() => {
  return [...notes.value]
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    .slice(0, 10)
})

const popularTags = computed(() => {
  const tagCounts = {}
  notes.value.forEach(note => {
    if (note.tags) {
      note.tags.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1
      })
    }
  })

  return Object.entries(tagCounts)
    .sort(([,a], [,b]) => b - a)
    .map(([tag]) => tag)
    .slice(0, 10)
})

// 메서드들
const sendQuickMessage = (message) => {
  currentMessage.value = message
  sendMessage()
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isLoading.value) return

  const userMessage = currentMessage.value.trim()
  currentMessage.value = ''

  // 사용자 메시지 추가
  messages.value.push({
    type: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  // AI 응답 준비
  const aiMessageIndex = messages.value.length
  messages.value.push({
    type: 'ai',
    content: '',
    isLoading: true,
    timestamp: new Date()
  })

  isLoading.value = true
  scrollToBottom()

  try {
    // API 호출
    const { chatAPI } = await import('../services/api.js')

    console.log('🧠 RAG 채팅 요청:', userMessage)
    const response = await chatAPI.ragChat(userMessage)

    // AI 응답 업데이트
    const aiResponse = response.data?.response ||
                      response.data?.data?.response ||
                      response.data?.ai_response ||
                      response.data?.data?.ai_response ||
                      '응답을 받을 수 없습니다.'

    messages.value[aiMessageIndex] = {
      type: 'ai',
      content: aiResponse,
      isLoading: false,
      timestamp: new Date(),
      relatedNotes: await findRelevantNotes(userMessage)
    }

    console.log('✅ AI 응답 완료')

  } catch (error) {
    console.error('❌ 채팅 오류:', error)
    messages.value[aiMessageIndex] = {
      type: 'ai',
      content: `죄송합니다. 오류가 발생했습니다: ${error.message}`,
      isLoading: false,
      timestamp: new Date()
    }
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const findRelevantNotes = async (query) => {
  try {
    const { notesAPI } = await import('../services/api.js')

    const searchData = {
      query: query.trim(),
      limit: 5
    }

    const searchResult = await notesAPI.search(searchData)

    let notes = []
    if (searchResult.data?.data?.results) {
      notes = searchResult.data.data.results
    } else if (searchResult.data?.results) {
      notes = searchResult.data.results
    } else if (Array.isArray(searchResult.data)) {
      notes = searchResult.data
    }

    return notes
  } catch (error) {
    console.error('관련 노트 검색 실패:', error)
    return []
  }
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const adjustTextareaHeight = () => {
  const textarea = messageInput.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
  }
}

const formatMessage = (content) => {
  if (!content) return ''

  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="italic text-gray-800">$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono text-purple-700">$1</code>')
    .replace(/###\s+(.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2 text-gray-900">$1</h3>')
    .replace(/##\s+(.*$)/gm, '<h2 class="text-xl font-semibold mt-6 mb-3 text-gray-900">$1</h2>')
    .replace(/#\s+(.*$)/gm, '<h1 class="text-2xl font-bold mt-8 mb-4 text-gray-900">$1</h1>')
    .replace(/\n/g, '<br>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content)
    // 간단한 피드백 (선택사항)
    console.log('✅ 클립보드에 복사됨')
  } catch (error) {
    console.error('❌ 복사 실패:', error)
  }
}

const continueConversation = (content) => {
  currentMessage.value = `"${content.slice(0, 100)}..." 이것에 대해 더 자세히 설명해줘`
  sendMessage()
}

const findRelatedNotes = async (content) => {
  const relatedNotes = await findRelevantNotes(content)
  if (relatedNotes.length > 0) {
    const notesList = relatedNotes.map(note => `• ${note.title}`).join('\n')
    currentMessage.value = `다음 노트들과 관련된 내용을 분석해줘:\n${notesList}`
    sendMessage()
  }
}

const openNote = (noteId) => {
  router.push(`/notes/${noteId}`)
}

const searchByTag = (tag) => {
  router.push(`/search?q=${encodeURIComponent('#' + tag)}`)
}

const refreshNotes = async () => {
  isRefreshing.value = true
  try {
    await notesStore.fetchNotes()
    notes.value = notesStore.notes
    console.log('✅ 노트 새로고침 완료')
  } catch (error) {
    console.error('❌ 노트 새로고침 실패:', error)
  } finally {
    isRefreshing.value = false
  }
}

const clearHistory = () => {
  if (confirm('대화 기록을 모두 삭제하시겠습니까?')) {
    messages.value = []
    console.log('✅ 대화 기록 삭제됨')
  }
}

const formatTime = (date) => {
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return '오늘'
  } else if (diffDays === 1) {
    return '어제'
  } else if (diffDays < 7) {
    return `${diffDays}일 전`
  } else {
    return date.toLocaleDateString('ko-KR')
  }
}

// 라이프사이클
onMounted(async () => {
  await refreshNotes()

  // 메시지 입력창에 포커스
  nextTick(() => {
    messageInput.value?.focus()
  })
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
