import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login', // <--- CAMBIADO: Ahora tiene su propia URL
      name: 'login',
      component: LoginView
    },
    {
      path: '/', // <--- MANTENIDO: El dashboard es la página principal
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/caja',
      name: 'caja',
      component: () => import('../views/CajaView.vue')
    },
    {
      path: '/inventario',
      name: 'inventario',
      component: () => import('../views/InventarioView.vue')
    },
    {
      path: '/pos',
      name: 'pos',
      component: () => import('../views/PosView.vue')
    },
    {
      path: '/reportes',
      name: 'reportes',
      component: () => import('../views/ReportesView.vue')
    }
  ]
})

export default router