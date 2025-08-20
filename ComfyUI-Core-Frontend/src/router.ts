import {
  // NavigationGuardNext,
  // RouteLocationNormalized,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router'

import LayoutDefault from '@/views/layouts/LayoutDefault.vue'

// 移除用户认证相关导入
// import { useUserStore } from './stores/userStore'
import { isElectron } from './utils/envUtil'

const isFileProtocol = window.location.protocol === 'file:'
const basePath = isElectron() ? '/' : window.location.pathname

// 移除guardElectronAccess - 不再需要桌面应用路由

const router = createRouter({
  history: isFileProtocol
    ? createWebHashHistory()
    : // Base path must be specified to ensure correct relative paths
      // Example: For URL 'http://localhost:7801/ComfyBackendDirect',
      // we need this base path or assets will incorrectly resolve from 'http://localhost:7801/'
      createWebHistory(basePath),
  routes: [
    {
      path: '/',
      component: LayoutDefault,
      children: [
        {
          path: '',
          name: 'GraphView',
          component: () => import('@/views/GraphView.vue'),
          // 移除用户认证检查，直接进入GraphView
          beforeEnter: (_to, _from, next) => {
            next()
          }
        }
        // 移除所有桌面应用和认证相关路由
      ]
    }
  ],

  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

export default router
