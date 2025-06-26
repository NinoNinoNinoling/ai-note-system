<template>
  <div class="space-y-6">
    <!-- 페이지 헤더 -->
    <div class="text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🔍 노트 검색</h1>
      <p class="text-gray-600">키워드나 내용으로 노트를 찾아보세요</p>
    </div>

    <!-- 검색 박스 -->
    <div class="max-w-2xl mx-auto">
      <div class="relative">
        <input
          ref="searchInput"
          v-model="searchQuery"
          @keyup.enter="performSearch"
          @input="handleSearchInput"
          type="text"
          placeholder="검색어를 입력하세요... (예: 'LangChain', 'AI 프로젝트')"
          class="w-full px-6 py-4 text-lg border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm"
        />
        <button
          @click="performSearch"
          :disabled="!searchQuery.trim() || isSearching"
          class="absolute right-3 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
        >
          <span v-if="isSearching">⏳</span>
          <span v-else>🔍</span>
        </button>
      </div>

      <!-- 검색 옵션 -->
      <div class="flex items-center justify-center space-x-6 mt-4">
        <label class="flex items-center space-x-2 cursor-pointer">
          <input
            v-model="searchMode"
            type="radio"
            value="text"
            class="text-blue-600 focus:ring-blue-500"
          />
          <span class="text-sm text-gray-700">📝 텍스트 검색</span>
        </label>
        <label class="flex items-center space-x-2 cursor-pointer">
          <input
            v-model="searchMode"
            type="radio"
            value="semantic"
            class="text-blue-600 focus:ring-blue-500"
          />
          <span class="text-sm text-gray-700">🧠 의미 검색 (RAG)</span>
        </label>
      </div>
    </div>

    <!-- 빠른 검색 태그 -->
    <div v-if="popularTags.length > 0" class="text-center">
      <p class="text-sm text-gray-600 mb-3">빠른 검색:</p>
      <div class="flex flex-wrap justify-center gap-2">
        <button
          v-for="tag in popularTags.slice(0, 10)"
          :key="tag"
          @click="searchByTag(tag)"
          class="px-3 py-1.5 bg-gray-100 hover:bg-blue-100 text-gray-700 hover:text-blue-700 rounded-full text-sm transition-colors"
        >
          #{{ tag }}
        </button>
      </div>
    </div>

    <!-- 검색 진행 상태 -->
    <div v-if="isSearching" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">
        {{ searchMode === 'semantic' ? 'AI가 의미를 분석하고 있습니다...' : '검색 중...' }}
      </p>
    </div>

    <!-- 검색 결과 -->
    <div v-else-if="searchResults.length > 0">
      <!-- 결과 헤더 -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-gray-900">
          검색 결과 ({{ searchResults.length }}개)
        </h2>
        <div class="text-sm text-gray-500">
          {{ searchMode === 'semantic' ? '🧠 AI 의미 검색' : '📝 텍스트 검색' }} 결과
        </div>
      </div>

      <!-- 결과 목록 -->
      <div class="space-y-4">
        <div
          v-for="(result, index) in searchResults"
          :key="result.id || index"
          class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md hover:border-blue-300 transition-all cursor-pointer"
          @click="openNote(result.id || result.note_id)"
        >
          <!-- 노트 제목 -->
          <h3 class="text-lg font-semibold text-gray-900 mb-2 hover:text-blue-600 transition-colors">
            {{ result.title || '제목 없음' }}
          </h3>

          <!-- 검색 점수 (의미 검색일 때) -->
          <div v-if="searchMode === 'semantic' && result.score" class="mb-2">
            <div class="flex items-center space-x-2">
              <span class="text-xs text-gray-500">관련도:</span>
              <div class="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                <div
                  class="bg-blue-600 h-2 rounded-full"
                  :style="{ width: `${Math.min(result.score * 100, 100)}%` }"
                ></div>
              </div>
              <span class="text-xs text-gray-500">{{ Math.round(result.score * 100) }}%</span>
            </div>
          </div>

          <!-- 노트 내용 미리보기 -->
          <div class="text-gray-600 text-sm mb-4">
            {{ getContentPreview(result.content) }}
          </div>

          <!-- 태그들 -->
          <div v-if="result.tags && result.tags.length > 0" class="flex flex-wrap gap-2 mb-3">
            <span
              v-for="tag in result.tags"
              :key="tag"
              class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
            >
              #{{ tag }}
            </span>
          </div>

          <!-- 메타 정보 -->
          <div class="flex items-center justify-between text-xs text-gray-500">
            <div class="flex items-center space-x-4">
              <span>📅 {{ formatDate(result.created_at || result.updated_at) }}</span>
              <span>📊 {{ getWordCount(result.content) }}단어</span>
            </div>
            <button
              @click.stop="openNote(result.id || result.note_id)"
              class="text-blue-600 hover:text-blue-800 font-medium"
            >
              열기 →
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 검색 결과 없음 -->
    <div v-else-if="hasSearched && !isSearching" class="text-center py-12">
      <div class="text-6xl mb-4">🔍</div>
      <h3 class="text-xl font-medium text-gray-900 mb-2">검색 결과가 없습니다</h3>
      <p class="text-gray-600 mb-6">
        "{{ lastSearchQuery }}"에 대한 결과를 찾을 수 없습니다.
      </p>
      <div class="space-y-2 text-sm text-gray-500">
        <p>• 다른 키워드로 검색해보세요</p>
        <p>• {{ searchMode === 'text' ? '의미 검색(RAG)' : '텍스트 검색' }}으로 바꿔보세요</p>
        <p>• 태그를 이용해 검색해보세요</p>
      </div>
    </div>

    <!-- 초기 상태 (검색 안함) -->
    <div v-else-if="!hasSearched" class="text-center py-12">
      <div class="text-6xl mb-4">💡</div>
      <h3 class="text-xl font-medium text-gray-900 mb-2">검색 팁</h3>
      <div class="space-y-2 text-gray-600 max-w-md mx-auto">
        <p><strong>📝 텍스트 검색:</strong> 정확한 단어나 구문을 찾습니다</p>
        <p><strong>🧠 의미 검색:</strong> AI가 내용의 의미를 이해해서 관련 노트를 찾습니다</p>
        <p><strong>🏷️ 태그 검색:</strong> 빠른 검색 태그를 클릭하세요</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNotesStore } from '../stores/notes'

const router = useRouter()
const route = useRoute()
const notesStore = useNotesStore()

// 검색 상태
const searchQuery = ref('')
const searchMode = ref('text') // 'text' | 'semantic'
const searchResults = ref([])
const isSearching = ref(false)
const hasSearched = ref(false)
const lastSearchQuery = ref('')
const searchInput = ref(null)

// 태그 데이터
const popularTags = ref([])

// 메서드들
const performSearch = async () => {
  const query = searchQuery.value.trim()
  if (!query || isSearching.value) return

  isSearching.value = true
  hasSearched.value = true
  lastSearchQuery.value = query

  try {
    console.log(`🔍 ${searchMode.value === 'semantic' ? 'AI 의미' : '텍스트'} 검색:`, query)

    const { notesAPI } = await import('../services/api.js')

    // 검색 데이터 구성
    const searchData = {
      query: query,
      mode: searchMode.value, // 'text' 또는 'semantic'
      limit: 20
    }

    const response = await notesAPI.search(searchData)

    // 응답 파싱
    let results = []
    if (response.data?.data?.results) {
      results = response.data.data.results
    } else if (response.data?.results) {
      results = response.data.results
    } else if (Array.isArray(response.data)) {
      results = response.data
    }

    searchResults.value = results
    console.log(`✅ ${results.length}개 검색 결과 찾음`)

  } catch (error) {
    console.error('❌ 검색 실패:', error)
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

const handleSearchInput = () => {
  // 실시간 검색은 너무 부하가 클 수 있으므로 제거
  // 사용자가 Enter를 누르거나 검색 버튼을 클릭할 때만 검색
}

const searchByTag = (tag) => {
  searchQuery.value = `#${tag}`
  searchMode.value = 'text'
  performSearch()
}

const openNote = (noteId) => {
  if (noteId) {
    router.push(`/notes/${noteId}`)
  }
}

const getContentPreview = (content) => {
  if (!content) return '내용 없음'

  const plainText = content
    .replace(/#{1,6}\s/g, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/`(.*?)`/g, '$1')
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/\n/g, ' ')
    .trim()

  return plainText.length > 200 ? plainText.slice(0, 200) + '...' : plainText
}

const getWordCount = (content) => {
  if (!content) return 0
  return content.split(/\s+/).filter(word => word.length > 0).length
}

const formatDate = (dateString) => {
  if (!dateString) return ''

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

const loadPopularTags = async () => {
  try {
    const tags = await notesStore.fetchTags()
    popularTags.value = tags.slice(0, 15) // 최대 15개까지만
  } catch (error) {
    console.error('태그 로드 실패:', error)
  }
}

// 라이프사이클
onMounted(async () => {
  // URL 쿼리에서 검색어 가져오기
  const urlQuery = route.query.q
  if (urlQuery) {
    searchQuery.value = urlQuery
    await nextTick()
    performSearch()
  }

  // 노트 데이터와 태그 로드
  await notesStore.fetchNotes()
  await loadPopularTags()

  // 검색창에 포커스
  nextTick(() => {
    searchInput.value?.focus()
  })
})
</script>

<style scoped>
/* 커스텀 스타일 */
.search-highlight {
  background-color: #fef3c7;
  padding: 0 2px;
  border-radius: 2px;
}
</style>
