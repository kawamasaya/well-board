import { createRouter, createWebHistory } from 'vue-router/auto'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    meta: {
      isPublic: true,
    },
    component: () => import('@/pages/Index.vue')
  },
  {
    path: '/home',
    component: () => import('@/pages/Home.vue')
  },
  {
    path: '/teams',
    component: () => import('@/pages/Teams.vue')
  },
  {
    path: '/users',
    component: () => import('@/pages/Users.vue')
  },
  {
    path: '/entries',
    component: () => import('@/pages/Entries.vue')
  },
  {
    path: '/team-entries',
    component: () => import('@/pages/TeamEntries.vue')
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  try {
    await authStore.verifyToken()

    // ログイン済みユーザーが / にアクセスした場合は /home にリダイレクト
    if (to.path === "/" && authStore.isAuthenticated) {
      next("/home")
      return
    }

    next()
  } catch (error) {
    authStore.logout()

    // 認証エラーの場合、/ にリダイレクト（ログインページとして扱う）
    if (to.path !== "/") {
      next({ path: '/', query: { redirect: to.fullPath } })
      return
    }

    next()
  }
})

export default router
