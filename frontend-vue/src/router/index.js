// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'

const routes = [
  { path: '/', name: 'login', component: LoginView },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router