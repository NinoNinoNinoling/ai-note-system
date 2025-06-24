<template>
  <div class="notes-view">
    <!-- 페이지 헤더 -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">My Notes</h1>
        <p class="text-gray-600">{{ noteCount }} notes</p>
      </div>

      <div class="flex items-center space-x-3 mt-4 lg:mt-0">
        <button
          @click="refreshNotes"
          :disabled="loading"
          class="px-4 py-2 text-gray-600 hover:text-blue-600 border border-gray-300 rounded-lg hover:border-blue-300 transition-colors disabled:opacity-50"
        >
          <span class="flex items-center space-x-2">
            <span>🔄</span>
            <span>Refresh</span>
          </span>
        </button>

        <router-link
          to="/notes/new"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
        >
          <span>✏️</span>
          <span>New Note</span>
        </router-link>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="flex items-center space-x-3">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="text-gray-600">Loading notes...</span>
      </div>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
      <div class="flex items-center">
        <span class="text-yellow-600 text-2xl mr-3">⚠️</span>
        <div>
          <h3 class="text-yellow-800 font-medium">Backend server not available</h3>
          <p class="text-yellow-600 text-sm mt-1">Showing sample data. Please start the backend server.</p>
          <button
            @click="refreshNotes"
            class="mt-2 text-yellow-600 hover:text-yellow-800 font-medium text-sm underline"
          >
            Try again
          </button>
        </div>
      </div>
    </div>

    <!-- 노트가 없는 경우 -->
    <div v-else-if="notes.length === 0" class="text-center py-12">
      <div class="text-6xl mb-4">📝</div>
      <h3 class="text-xl font-medium text-gray-900 mb-2">No notes yet</h3>
      <p class="text-gray-600 mb-6">Start by creating your first note!</p>
      <router-link
        to="/notes/new"
        class="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
      >
        <span class="mr-2">✏️</span>
        Create your first note
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
              {{ note.title || 'Untitled Note' }}
            </h3>

            <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                @click.stop="editNote(note)"
                class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Edit note"
              >
                ✏️
              </button>
              <button
                @click.stop="deleteNote(note)"
                class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete note"
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
              <span>{{ getWordCount(note.content) }} words</span>
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
  if (confirm(`"${note.title || 'Untitled Note'}"를 삭제하시겠습니까?`)) {
    try {
      await notesStore.deleteNote(note.id)
      console.log('✅ 노트 삭제 완료')
    } catch (error) {
      console.error('❌ 노트 삭제 실패:', error)
    }
  }
}

const getContentPreview = (content) => {
  if (!content) return 'No content'

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
    return 'Today'
  } else if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays}d ago`
  } else {
    return date.toLocaleDateString()
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
