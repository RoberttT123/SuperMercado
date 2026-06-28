import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '@/views/LoginView.vue'

// Rutas que solo puede ver el admin
const rutasAdmin = ['dashboard', 'caja', 'inventario', 'reportes', 'proveedores']

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiereAuth: true, soloAdmin: true }
    },
    {
      path: '/caja',
      name: 'caja',
      component: () => import('../views/CajaView.vue'),
      meta: { requiereAuth: true, soloAdmin: true }
    },
    {
      path: '/inventario',
      name: 'inventario',
      component: () => import('../views/InventarioView.vue'),
      meta: { requiereAuth: true, soloAdmin: true }
    },
    {
      path: '/pos',
      name: 'pos',
      component: () => import('../views/PosView.vue'),
      meta: { requiereAuth: true, soloAdmin: true }
    },
    {
      path: '/reportes',
      name: 'reportes',
      component: () => import('../views/ReportesView.vue'),
      meta: { requiereAuth: true, soloAdmin: true }
    },
    {
      path: '/proveedores',
      name: 'proveedores',
      component: () => import('../views/ProveedoresView.vue'),
      meta: { requiereAuth: true, soloAdmin: true }
    },
    {
      path: '/pedidos',
      name: 'pedidos',
      component: () => import('../views/PedidosView.vue'),
      meta: { requiereAuth: true }  // ← accesible para todos los roles
    },
    {
      // Captura cualquier URL no definida
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ]
})

// ─── GUARDIA GLOBAL ───────────────────────────────────────────────────
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const role = user?.role || null

  // 1. Si no está logueado y la ruta requiere auth → al login
  if (to.meta.requiereAuth && !token) {
    return next({ name: 'login' })
  }

  // 2. Si ya está logueado e intenta ir al login → redirigir según rol
  if (to.name === 'login' && token) {
    return next(role === 'admin' ? { name: 'dashboard' } : { name: 'pedidos' })
  }

  // 3. Si es vendedor e intenta acceder a ruta solo admin → a pedidos
  if (to.meta.soloAdmin && role === 'vendedor') {
    return next({ name: 'pedidos' })
  }

  next()
})

export default router