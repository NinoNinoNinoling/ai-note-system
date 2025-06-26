<template>
  <div class="h-full flex flex-col bg-gray-50">
    <!-- 채팅 헤더 -->
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded flex items-center justify-center">
          <span class="text-white text-xs">🤖</span>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-900">AI Assistant</h3>
          <p class="text-xs text-gray-500">{{ isRAGMode ? 'RAG 모드' : '일반 채팅' }}</p>
        </div>
      </div>

      <!-- 간단한 컨트롤 -->
      <div class="flex items-center space-x-2">
        <button
          @click="toggleRAGMode"
          :class="[
            'text-xs px-2 py-1 rounded transition-colors',
            isRAGMode ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
          title="RAG 모드 토글"
        >
          {{ isRAGMode ? '📚 RAG' : '💬 Chat' }}
        </button>

        <button
          @click="clearChat"
          class="text-xs px-2 py-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
          title="채팅 초기화"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- 채팅 메시지들 -->
    <div
      ref="chatContainer"
      class="flex-1 overflow-y-auto p-3 space-y-3 text-sm"
    >
      <!-- 시작 메시지 -->
      <div v-if="messages.length === 0" class="text-center py-8">
        <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mx-auto mb-3 flex items-center justify-center">
          <span class="text-white">🤖</span>
        </div>
        <h4 class="font-medium text-gray-900 mb-2">AI 어시스턴트</h4>
        <p class="text-xs text-gray-500 mb-3">
          {{ isRAGMode ? '현재 노트를 기반으로 답변합니다' : '자유롭게 질문해보세요' }}
        </p>

        <!-- 빠른 액션들 -->
        <div class="space-y-1">
          <button
            @click="sendQuickMessage('이 노트를 요약해줘')"
            class="block w-full text-xs bg-white border border-gray-200 rounded-lg py-2 px-3 hover:bg-gray-50 transition-colors"
          >
            📝 노트 요약
          </button>
          <button
            @click="sendQuickMessage('이 내용을 개선해줘')"
            class="block w-full text-xs bg-white border border-gray-200 rounded-lg py-2 px-3 hover:bg-gray-50 transition-colors"
          >
            ✨ 내용 개선
          </button>
          <button
            @click="sendQuickMessage('관련된 아이디어를 추천해줘')"
            class="block w-full text-xs bg-white border border-gray-200 rounded-lg py-2 px-3 hover:bg-gray-50 transition-colors"
          >
            💡 아이디어 추천
          </button>
        </div>
      </div>

      <!-- 메시지 리스트 -->
      <div v-for="(message, index) in messages" :key="index">
        <!-- 사용자 메시지 -->
        <div v-if="message.type === 'user'" class="flex justify-end">
          <div class="max-w-[85%] bg-blue-600 text-white px-3 py-2 rounded-lg rounded-br-md text-sm">
            {{ message.content }}
          </div>
        </div>

        <!-- AI 응답 -->
        <div v-else class="flex justify-start">
          <div class="flex space-x-2 max-w-[90%]">
            <div class="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
              <span class="text-white text-xs">🤖</span>
            </div>
            <div class="bg-white border border-gray-200 px-3 py-2 rounded-lg rounded-tl-md">
              <div
                v-if="message.content"
                class="text-sm leading-relaxed"
                v-html="formatAIMessage(message.content)"
              ></div>
              <div v-if="message.isLoading" class="flex items-center space-x-2">
                <div class="flex space-x-1">
                  <div class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                  <div class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
                <span class="text-xs text-gray-500">생각 중...</span>
              </div>

              <!-- AI 응답에 액션 버튼들 -->
              <div v-if="message.content && !message.isLoading" class="flex space-x-1 mt-2">
                <button
                  @click="insertToNote(message.content)"
                  class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                  title="노트에 삽입"
                >
                  📝 Insert
                </button>
                <button
                  @click="copyMessage(message.content)"
                  class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                  title="복사"
                >
                  📋 Copy
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 입력 영역 -->
    <div class="bg-white border-t border-gray-200 p-3">
      <div class="relative">
        <textarea
          ref="messageInput"
          v-model="currentMessage"
          @keydown="handleChatKeydown"
          @input="adjustChatTextarea"
          :disabled="isLoading"
          :placeholder="isRAGMode ? '노트 관련 질문...' : '메시지 입력...'"
          class="w-full px-3 py-2 pr-8 text-sm border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
          rows="1"
        ></textarea>

        <button
          @click="sendChatMessage"
          :disabled="!currentMessage.trim() || isLoading"
          :class="[
            'absolute right-1 top-1/2 transform -translate-y-1/2 w-6 h-6 rounded flex items-center justify-center transition-colors text-xs',
            currentMessage.trim() && !isLoading
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          ]"
        >
          <span v-if="!isLoading">↑</span>
          <div v-else class="w-3 h-3 border border-gray-400 border-t-white rounded-full animate-spin"></div>
        </button>
      </div>

      <div class="text-xs text-gray-500 mt-1 text-center">
        Enter 전송 • Shift+Enter 줄바꿈
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AIChatPanel',
  props: {
    noteContent: {
      type: String,
      default: ''
    }
  },
  emits: ['insert-to-note'],
  data() {
    return {
      messages: [],
      currentMessage: '',
      isLoading: false,
      isRAGMode: true
    }
  },
  methods: {
    toggleRAGMode() {
      this.isRAGMode = !this.isRAGMode
      console.log(`🔄 RAG 모드: ${this.isRAGMode ? '활성화' : '비활성화'}`)
    },

    sendQuickMessage(message) {
      this.currentMessage = message
      this.sendChatMessage()
    },

    async sendChatMessage() {
      if (!this.currentMessage.trim() || this.isLoading) return

      const userMessage = this.currentMessage.trim()
      this.currentMessage = ''

      // 사용자 메시지 추가
      this.messages.push({
        type: 'user',
        content: userMessage,
        timestamp: new Date()
      })

      // AI 응답 준비
      const aiMessageIndex = this.messages.length
      this.messages.push({
        type: 'ai',
        content: '',
        isLoading: true,
        timestamp: new Date()
      })

      this.isLoading = true
      this.scrollToBottom()

      try {
        // API 동적 import - 올바른 구조 사용
        const apiModule = await import('../services/api.js')
        const { chatAPI } = apiModule

        let response
        if (this.isRAGMode && this.noteContent.trim()) {
          // RAG 모드: 노트 내용과 함께 전송
          console.log('🧠 RAG 채팅 요청:', userMessage)
          response = await chatAPI.ragChat(`노트 내용:\n${this.noteContent}\n\n질문: ${userMessage}`)
        } else {
          // 일반 채팅
          console.log('💬 일반 채팅 요청:', userMessage)
          response = await chatAPI.chat(userMessage)
        }

        // AI 응답 업데이트 - 안전한 응답 파싱
        const aiResponse = response.data?.response ||
                          response.data?.data?.response ||
                          response.data?.ai_response ||
                          response.data?.data?.ai_response ||
                          '응답을 받을 수 없습니다.'

        this.messages[aiMessageIndex] = {
          type: 'ai',
          content: aiResponse,
          isLoading: false,
          timestamp: new Date()
        }

        console.log('✅ AI 응답 완료')

      } catch (error) {
        console.error('❌ 채팅 오류:', error)
        this.messages[aiMessageIndex] = {
          type: 'ai',
          content: `죄송합니다. 오류가 발생했습니다: ${error.message}`,
          isLoading: false,
          timestamp: new Date()
        }
      } finally {
        this.isLoading = false
        this.scrollToBottom()
      }
    },

    handleChatKeydown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        this.sendChatMessage()
      }
    },

    adjustChatTextarea() {
      const textarea = this.$refs.messageInput
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px'
      }
    },

    formatAIMessage(content) {
      if (!content) return ''

      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded text-xs font-mono">$1</code>')
        .replace(/\n/g, '<br>')
    },

    insertToNote(content) {
      console.log('📝 노트에 삽입:', content)
      this.$emit('insert-to-note', content)
    },

    async copyMessage(content) {
      try {
        await navigator.clipboard.writeText(content)
        console.log('📋 클립보드에 복사됨')

        // 시각적 피드백
        const button = event.target
        const originalText = button.textContent
        button.textContent = '✅ Copied'
        button.classList.add('bg-green-100', 'text-green-700')
        button.classList.remove('bg-gray-100', 'text-gray-700')

        setTimeout(() => {
          button.textContent = originalText
          button.classList.remove('bg-green-100', 'text-green-700')
          button.classList.add('bg-gray-100', 'text-gray-700')
        }, 1500)
      } catch (error) {
        console.error('클립보드 복사 실패:', error)
      }
    },

    clearChat() {
      this.messages = []
      console.log('🗑️ 채팅 초기화됨')
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.chatContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    }
  },

  watch: {
    noteContent() {
      // 노트 내용이 변경될 때마다 RAG 모드에서 업데이트된 컨텍스트 사용
      if (this.isRAGMode) {
        console.log('📝 노트 내용 업데이트됨 (RAG 컨텍스트 갱신)')
      }
    }
  }
}
</script>

<style scoped>
/* 커스텀 스크롤바 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 애니메이션 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
</style>
