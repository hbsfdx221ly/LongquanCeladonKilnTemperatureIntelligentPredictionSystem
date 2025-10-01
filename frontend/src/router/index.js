import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Kiln3D from '../views/Kiln3D.vue'
import DataAnalysis from '../views/DataAnalysis.vue'
import BatchManagement from '../views/BatchManagement.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页' }
  },
  {
    path: '/kiln-3d',
    name: 'Kiln3D',
    component: Kiln3D,
    meta: { title: '3D窑炉模型' }
  },
  {
    path: '/data-analysis',
    name: 'DataAnalysis',
    component: DataAnalysis,
    meta: { title: '数据分析' }
  },
  {
    path: '/batch-management',
    name: 'BatchManagement',
    component: BatchManagement,
    meta: { title: '批次管理' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 瓷路算法`
  }
  next()
})

export default router
