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
    // ── ADMIN + CAJERO (personal mínimo: el cajero ve todo lo de gestión) ──
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiereAuth: true, roles: ['admin', 'cajero'] }
    },
    {
      path: '/inventario',
      name: 'inventario',
      component: () => import('../views/InventarioView.vue'),
      meta: { requiereAuth: true, roles: ['admin', 'cajero'] }
    },
    {
      path: '/reportes',
      name: 'reportes',
      component: () => import('../views/ReportesView.vue'),
      meta: { requiereAuth: true, roles: ['admin', 'cajero'] }
    },
    {
      path: '/proveedores',
      name: 'proveedores',
      component: () => import('../views/ProveedoresView.vue'),
      meta: { requiereAuth: true, roles: ['admin', 'cajero'] }
    },
    // ── ADMIN + CAJERO ───────────────────────────────
    {
      path: '/caja',
      name: 'caja',
      component: () => import('../views/CajaView.vue'),
      meta: { requiereAuth: true, roles: ['admin', 'cajero'] }
    },
    {
      path: '/pos',
      name: 'pos',
      component: () => import('../views/PosView.vue'),
      meta: { requiereAuth: true, roles: ['admin', 'cajero'] }
    },
    // ── TODOS LOS ROLES ──────────────────────────────
    {
      path: '/clientes',
      name: 'clientes',
      component: () => import('../views/ClientesView.vue'),
      meta: { requiereAuth: true, roles: ['admin', 'cajero', 'vendedor'] }
    },
    // ── SOLO VENDEDOR ────────────────────────────────
    {
      path: '/pedidos',
      name: 'pedidos',
      component: () => import('../views/PedidosView.vue'),
      meta: { requiereAuth: true, roles: ['vendedor'] }
    },
    // ── Catch-all ────────────────────────────────────
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ]
})

// ─── GUARDIA GLOBAL ───────────────────────────────────────────────────

// Pantalla por defecto de cada rol al iniciar sesión o al intentar
// entrar a una ruta que no le corresponde.
const destinoPorDefecto = {
  admin: { name: 'dashboard' },
  cajero: { name: 'dashboard' },
  vendedor: { name: 'pedidos' }
}

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const role = user?.role || null

  // 1. Sin token → login
  if (to.meta.requiereAuth && !token) {
    return next({ name: 'login' })
  }

  // 2. Ya logueado intenta ir al login → redirigir según su rol
  if (to.name === 'login' && token) {
    return next(destinoPorDefecto[role] || { name: 'login' })
  }

  // 3. Ruta restringida por rol y el usuario no está autorizado → a su pantalla por defecto
  if (to.meta.roles && !to.meta.roles.includes(role)) {
    return next(destinoPorDefecto[role] || { name: 'login' })
  }

  next()
})

export default router