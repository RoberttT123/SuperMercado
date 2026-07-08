import { createRouter, createWebHashHistory } from 'vue-router'  
import DashboardView from '../views/DashboardView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL), 
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    // ── SOLO ADMIN ──────────────────────────────────
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
    // ── SOLO VENDEDOR ────────────────────────────────
    {
      path: '/pedidos',
      name: 'pedidos',
      component: () => import('../views/PedidosView.vue'),
      meta: { requiereAuth: true, soloVendedor: true }
    },
    // ── Catch-all ────────────────────────────────────
    {
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

  // 1. Sin token → login
  if (to.meta.requiereAuth && !token) {
    return next({ name: 'login' })
  }

  // 2. Ya logueado intenta ir al login → redirigir según rol
  if (to.name === 'login' && token) {
    return next(role === 'admin' ? { name: 'dashboard' } : { name: 'pedidos' })
  }

  // 3. Vendedor intenta ruta de admin → a pedidos
  if (to.meta.soloAdmin && role === 'vendedor') {
    return next({ name: 'pedidos' })
  }

  // 4. Admin intenta ruta de vendedor → a dashboard
  if (to.meta.soloVendedor && role === 'admin') {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router