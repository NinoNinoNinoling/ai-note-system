<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 헤더 -->
    <header class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- 로고 및 네비게이션 -->
          <div class="flex items-center space-x-8">
            <!-- 클릭 가능한 로고 -->
            <router-link
              to="/notes"
              class="flex items-center hover:opacity-80 transition-opacity cursor-pointer"
            >
              <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">🧠</span>
              </div>
              <h1 class="ml-3 text-xl font-bold text-gray-900">AI 노트 시스템</h1>
            </router-link>

            <!-- 네비게이션 메뉴 -->
            <nav class="hidden md:flex space-x-8">
              <router-link
                to="/notes"
                class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="{ 'text-blue-600 bg-blue-50': $route.path.startsWith('/notes') }"
              >
                📝 노트
              </router-link>
              <router-link
                to="/chat"
                class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="{ 'text-blue-600 bg-blue-50': $route.path === '/chat' }"
              >
                🤖 AI 채팅
              </router-link>
              <router-link
                to="/search"
                class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="{ 'text-blue-600 bg-blue-50': $route.path === '/search' }"
              >
                🔍 검색
              </router-link>
            </nav>
          </div>

          <!-- 우측 액션 버튼들 -->
          <div class="flex items-center space-x-4">
            <!-- 빠른 검색 -->
            <div class="relative">
              <input
                v-model="quickSearch"
                @keyup.enter="performQuickSearch"
                type="text"
                placeholder="빠른 검색..."
                class="w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
              <button
                @click="performQuickSearch"
                class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-blue-600"
              >
                🔍
              </button>
            </div>

            <!-- 새 노트 버튼 -->
            <button
              @click="createNewNote"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
            >
              <span>✏️</span>
              <span>새 노트</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 라우터 뷰 -->
      <router-view />
    </main>

    <!-- 로딩 오버레이 -->
    <div
      v-if="loading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span class="text-gray-700">로딩 중...</span>
      </div>
    </div>

    <!-- 알림 토스트 -->
    <div
      v-if="notification.show"
      class="fixed top-4 right-4 z-50 max-w-sm"
    >
      <div
        class="rounded-lg shadow-lg p-4 transition-all duration-300"
        :class="{
          'bg-green-500 text-white': notification.type === 'success',
          'bg-red-500 text-white': notification.type === 'error',
          'bg-blue-500 text-white': notification.type === 'info'
        }"
      >
        <div class="flex items-center justify-between">
          <span>{{ notification.message }}</span>
          <button @click="notification.show = false" class="ml-2 text-white hover:text-gray-200">
            ✕
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotesStore } from './stores/notes'

const router = useRouter()
const notesStore = useNotesStore()

// 반응형 상태
const quickSearch = ref('')
const loading = ref(false)

const notification = reactive({
  show: false,
  message: '',
  type: 'info' // success, error, info
})

// 빠른 검색
const performQuickSearch = () => {
  if (quickSearch.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(quickSearch.value)}`)
    quickSearch.value = ''
  }
}

// 새 노트 생성
const createNewNote = () => {
  router.push('/notes/new')
}

// 전역 알림 함수
const showNotification = (message, type = 'info') => {
  notification.message = message
  notification.type = type
  notification.show = true

  // 3초 후 자동 숨김
  setTimeout(() => {
    notification.show = false
  }, 3000)
}

// 전역 로딩 상태
const setLoading = (state) => {
  loading.value = state
}

// 앱 초기화
onMounted(async () => {
  try {
    setLoading(true)
    // 초기 데이터 로드
    await notesStore.fetchNotes()
    showNotification('AI 노트 시스템에 오신 것을 환영합니다! 🎉', 'success')
  } catch (error) {
    console.error('초기화 에러:', error)
    showNotification('초기 데이터 로드에 실패했습니다', 'error')
  } finally {
    setLoading(false)
  }
})

// 전역으로 노출 (다른 컴포넌트에서 사용 가능)
window.app = {
  showNotification,
  setLoading
}
</script>

<style scoped>
/* 라우터 링크 활성 상태 */
.router-link-active {
  @apply text-blue-600 bg-blue-50;
}

/* 커스텀 스크롤바 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
