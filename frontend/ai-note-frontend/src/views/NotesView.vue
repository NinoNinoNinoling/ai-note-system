<template>
  <div class="space-y-6">
    <!-- 페이지 헤더 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">📝 내 노트</h1>
        <p class="text-gray-600 mt-1">
          {{ noteCount > 0 ? `총 ${noteCount}개의 노트` : '아직 노트가 없습니다' }}
        </p>
      </div>

      <div class="flex items-center space-x-3">
        <button
          @click="refreshNotes"
          :disabled="loading"
          class="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
        >
          <span class="text-lg">🔄</span>
          <span>새로고침</span>
        </button>

        <router-link
          to="/notes/new"
          class="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          <span>✏️</span>
          <span>새 노트</span>
        </router-link>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">노트를 불러오는 중...</p>
      </div>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-center">
        <span class="text-2xl mr-3">⚠️</span>
        <div>
          <h3 class="text-lg font-medium text-red-800">연결 오류</h3>
          <p class="text-red-600 text-sm">백엔드 서버를 시작해주세요.</p>
          <button
            @click="refreshNotes"
            class="mt-2 text-red-600 hover:text-red-800 font-medium text-sm underline"
          >
            다시 시도
          </button>
        </div>
      </div>
    </div>

    <!-- 노트가 없는 경우 -->
    <div v-else-if="notes.length === 0" class="text-center py-12">
      <div class="text-6xl mb-4">📝</div>
      <h3 class="text-xl font-medium text-gray-900 mb-2">아직 노트가 없습니다</h3>
      <p class="text-gray-600 mb-6">첫 번째 노트를 작성해보세요!</p>
      <router-link
        to="/notes/new"
        class="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
      >
        <span class="mr-2">✏️</span>
        첫 노트 작성하기
      </router-link>
    </div>

    <!-- 노트 그리드 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="note in notes"
        :key="note.id"
        class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all duration-200 cursor-pointer group"
        @click="editNote(note)"
      >
        <!-- 카드 헤더 -->
        <div class="p-6 pb-4">
          <div class="flex items-start justify-between mb-3">
            <h3 class="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-2">
              {{ note.title || '제목 없음' }}
            </h3>

            <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                @click.stop="editNote(note)"
                class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="노트 편집"
              >
                ✏️
              </button>
              <button
                @click.stop="deleteNote(note)"
                class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="노트 삭제"
              >
                🗑️
              </button>
            </div>
          </div>

          <!-- 노트 미리보기 -->
          <div class="text-gray-600 text-sm line-clamp-3 mb-4">
            {{ getContentPreview(note.content) }}
          </div>

          <!-- 태그들 -->
          <div v-if="note.tags && note.tags.length > 0" class="flex flex-wrap gap-2 mb-4">
            <span
              v-for="tag in note.tags"
              :key="tag"
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              #{{ tag }}
            </span>
          </div>
        </div>

        <!-- 카드 푸터 -->
        <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 rounded-b-lg">
          <div class="flex items-center justify-between text-xs text-gray-500">
            <div class="flex items-center space-x-1">
              <span>📅</span>
              <span>{{ formatDate(note.created_at) }}</span>
            </div>
            <div class="flex items-center space-x-1">
              <span>📊</span>
              <span>{{ getWordCount(note.content) }}단어</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotesStore } from '../stores/notes'

const router = useRouter()
const notesStore = useNotesStore()

// 컴퓨티드 속성들
const notes = computed(() => notesStore.notes)
const noteCount = computed(() => notesStore.noteCount)
const loading = computed(() => notesStore.loading)
const error = computed(() => notesStore.error)

// 메서드들
const refreshNotes = async () => {
  try {
    await notesStore.fetchNotes()
  } catch (error) {
    console.error('새로고침 실패:', error)
  }
}

const editNote = (note) => {
  router.push(`/notes/${note.id}`)
}

const deleteNote = async (note) => {
  if (confirm(`"${note.title || '제목 없는 노트'}"를 삭제하시겠습니까?`)) {
    try {
      await notesStore.deleteNote(note.id)
      console.log('✅ 노트 삭제 완료')
    } catch (error) {
      console.error('❌ 노트 삭제 실패:', error)
    }
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

  return plainText.length > 150 ? plainText.slice(0, 150) + '...' : plainText
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

// 라이프사이클
onMounted(async () => {
  await refreshNotes()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
