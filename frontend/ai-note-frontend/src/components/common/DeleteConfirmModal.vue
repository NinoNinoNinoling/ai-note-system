<template>
  <!-- 모달 오버레이 -->
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    @click="$emit('cancel')"
  >
    <!-- 모달 컨텐츠 -->
    <div
      class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 transform transition-all duration-200"
      @click.stop
    >
      <!-- 모달 헤더 -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
            <span class="text-red-600 text-xl">⚠️</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-900">
            Delete Note
          </h3>
        </div>

        <button
          @click="$emit('cancel')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <span class="text-xl">✕</span>
        </button>
      </div>

      <!-- 모달 바디 -->
      <div class="p-6">
        <p class="text-gray-600 mb-4">
          Are you sure you want to delete this note? This action cannot be undone.
        </p>

        <!-- 노트 정보 미리보기 -->
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 class="font-medium text-gray-900 mb-2">
            {{ note.title || 'Untitled Note' }}
          </h4>

          <div class="text-sm text-gray-600 mb-3">
            {{ contentPreview }}
          </div>

          <!-- 노트 메타 정보 -->
          <div class="flex items-center justify-between text-xs text-gray-500">
            <div class="flex items-center space-x-4">
              <span>📅 Created {{ formatDate(note.created_at) }}</span>
              <span>🔄 Updated {{ formatDate(note.updated_at) }}</span>
            </div>

            <div v-if="note.tags && note.tags.length > 0" class="flex items-center space-x-1">
              <span>🏷️</span>
              <span>{{ note.tags.length }} tags</span>
            </div>
          </div>
        </div>

        <!-- 경고 메시지 -->
        <div class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-start space-x-2">
            <span class="text-red-500 text-sm">⚠️</span>
            <div class="text-red-700 text-sm">
              <p class="font-medium">This will permanently delete:</p>
              <ul class="mt-1 list-disc list-inside text-xs space-y-1">
                <li>The note content and metadata</li>
                <li>All associated tags and links</li>
                <li>Related chat history mentioning this note</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 모달 푸터 -->
      <div class="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50 rounded-b-lg">
        <button
          @click="$emit('cancel')"
          class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          Cancel
        </button>

        <button
          @click="confirmDelete"
          :disabled="loading"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:ring-2 focus:ring-red-500 focus:ring-offset-2 flex items-center space-x-2"
        >
          <span v-if="loading" class="animate-spin">⏳</span>
          <span v-else>🗑️</span>
          <span>{{ loading ? 'Deleting...' : 'Delete Note' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  note: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const loading = ref(false)

// 컴퓨티드 속성들
const contentPreview = computed(() => {
  if (!props.note.content) return 'No content'

  // 마크다운 제거하고 텍스트만 추출
  const plainText = props.note.content
    .replace(/#{1,6}\s/g, '') // 헤더 제거
    .replace(/\*\*(.*?)\*\*/g, '$1') // 볼드 제거
    .replace(/\*(.*?)\*/g, '$1') // 이탤릭 제거
    .replace(/`(.*?)`/g, '$1') // 인라인 코드 제거
    .replace(/\[(.*?)\]\(.*?\)/g, '$1') // 링크 제거
    .replace(/\n/g, ' ') // 줄바꿈을 공백으로
    .trim()

  return plainText.length > 100 ? plainText.slice(0, 100) + '...' : plainText
})

// 날짜 포맷팅 함수
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'

  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 삭제 확인
const confirmDelete = async () => {
  loading.value = true

  try {
    // 약간의 지연을 두어 사용자가 로딩 상태를 볼 수 있도록
    await new Promise(resolve => setTimeout(resolve, 500))

    emit('confirm')
  } catch (error) {
    console.error('삭제 중 오류:', error)
  } finally {
    loading.value = false
  }
}

// ESC 키로 모달 닫기
const handleKeyDown = (event) => {
  if (event.key === 'Escape') {
    emit('cancel')
  }
}

// 컴포넌트 마운트 시 키보드 이벤트 리스너 추가
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  // 모달이 열릴 때 body 스크롤 방지
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
  // 모달이 닫힐 때 body 스크롤 복원
  document.body.style.overflow = 'auto'
})
</script>

<style scoped>
/* 모달 애니메이션 */
.modal-enter-active, .modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* 백드롭 애니메이션 */
.backdrop-enter-active, .backdrop-leave-active {
  transition: opacity 0.3s ease;
}

.backdrop-enter-from, .backdrop-leave-to {
  opacity: 0;
}

/* 포커스 링 커스터마이징 */
button:focus {
  outline: none;
}

/* 로딩 스피너 애니메이션 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* 반응형 디자인 */
@media (max-width: 640px) {
  .modal-content {
    margin: 1rem;
    max-width: calc(100vw - 2rem);
  }
}

/* 다크 모드 지원 (향후) */
@media (prefers-color-scheme: dark) {
  .bg-white {
    @apply bg-gray-800;
  }

  .text-gray-900 {
    @apply text-gray-100;
  }

  .text-gray-600 {
    @apply text-gray-300;
  }

  .border-gray-200 {
    @apply border-gray-700;
  }
}
</style>
