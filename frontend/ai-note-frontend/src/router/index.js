import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/notes'
  },
  {
    path: '/notes',
    name: 'Notes',
    component: () => import('../views/NotesView.vue'),
    meta: {
      title: 'My Notes'
    }
  },
  {
    path: '/notes/new',
    name: 'NewNote',
    component: () => import('../views/NoteEditor.vue'),
    meta: {
      title: 'New Note'
    }
  },
  {
    path: '/notes/:id',
    name: 'EditNote',
    component: () => import('../views/NoteEditor.vue'),
    props: true,
    meta: {
      title: 'Edit Note'
    }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/ChatView.vue'),
    meta: {
      title: 'AI Chat'
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/SearchView.vue'),
    meta: {
      title: 'Search Notes'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: 'Page Not Found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 네비게이션 가드
router.beforeEach((to, from, next) => {
  // 페이지 타이틀 설정
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI Note System`
  } else {
    document.title = 'AI Note System'
  }

  next()
})

export default router
