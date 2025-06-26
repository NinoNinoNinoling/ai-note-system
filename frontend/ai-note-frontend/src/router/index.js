import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/notes'
  },
  {
    path: '/notes',
    name: 'Notes',
    component: () => import('../views/NotesView.vue')
  },
  {
    path: '/notes/new',
    name: 'NewNote',
    component: () => import('../views/NoteEditor.vue')
  },
  {
    path: '/notes/:id',
    name: 'NoteDetail',
    component: () => import('../views/NoteEditor.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/ChatView.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/SearchView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
