<template>

  <!-- ═══════════════════════════════════════
       VENDEDOR — Overlay móvil
  ════════════════════════════════════════ -->
  <div v-if="!esAdmin">

    <!-- Botón flotante abrir -->
    <button
      v-if="!sidebarAbierto"
      @click="sidebarAbierto = true"
      class="fixed top-4 left-4 z-50 w-10 h-10 bg-[#FF6B2B] text-white rounded-xl shadow-lg flex items-center justify-center font-black text-sm hover:bg-[#E85510] transition-colors"
    >
      ☰
    </button>

    <!-- Overlay oscuro -->
    <div
      v-if="sidebarAbierto"
      @click="sidebarAbierto = false"
      class="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
    ></div>

    <!-- Panel vendedor -->
    <aside
      :class="[
        sidebarAbierto ? 'translate-x-0' : '-translate-x-full',
        'fixed top-0 left-0 h-screen w-[280px] z-50 bg-gradient-to-b from-[#FFF9F6] to-[#FFE4D6] border-r-2 border-[#FFD0B8] flex flex-col justify-between shadow-2xl transition-transform duration-300'
      ]"
    >
      <div>
        <!-- Header -->
        <div class="bg-gradient-to-br from-[#FF6B2B] to-[#E85510] pt-4 pb-6 px-5 text-center rounded-b-[28px] relative">
          <button
            @click="sidebarAbierto = false"
            class="absolute top-3 right-3 w-8 h-8 bg-white/20 text-white rounded-lg flex items-center justify-center hover:bg-white/30 transition-colors font-black"
          >✕</button>

          <img src="/src/assets/logo.png" alt="Logo"
            class="w-20 h-20 object-cover rounded-full mx-auto block mb-3 bg-white border-4 border-white/30"
            @error="handleImageError" v-if="hasLogo"
          />
          <div v-else class="w-20 h-20 rounded-full mx-auto mb-3 bg-white flex items-center justify-center text-3xl">🛒</div>

          <h1 class="text-white font-black text-base tracking-wide uppercase">Almacen Cori</h1>
          <p class="text-white/70 text-xs italic mt-1">Precio, calidad y confianza.</p>
        </div>

        <!-- Info vendedor -->
        <div class="mx-4 mt-5 bg-white rounded-2xl p-4 border border-[#FFE0CC] shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-[#FFF3EE] rounded-full flex items-center justify-center text-xl border border-[#FFE0CC]">
              👤
            </div>
            <div>
              <div class="font-black text-[#2A1A0A] text-sm">{{ authStore.user?.username }}</div>
              <div class="text-xs text-[#FF6B2B] font-bold uppercase tracking-wide">Vendedor</div>
            </div>
          </div>
        </div>

        <!-- Menú vendedor -->
        <div class="mt-6 px-4">
          <div class="text-[10px] font-extrabold tracking-widest uppercase text-[#A09088] mb-3 px-1">
            Mis opciones
          </div>
          <nav class="flex flex-col gap-2">
            <router-link
              to="/pedidos"
              @click="sidebarAbierto = false"
              class="nav-link-vendedor"
              active-class="nav-active-vendedor"
            >
              <span class="text-2xl">📋</span>
              <div>
                <div class="font-bold text-sm">Mis Pedidos</div>
                <div class="text-xs text-gray-400">Preventa y gestión de entregas</div>
              </div>
            </router-link>
          </nav>
        </div>
      </div>

      <!-- Footer vendedor -->
      <div class="p-4">
        <button
          @click="handleLogout"
          class="w-full flex items-center justify-center gap-2 bg-red-50 hover:bg-red-100 text-red-500 font-bold py-3 rounded-xl transition-colors border border-red-200"
        >
          🚪 Cerrar Sesión
        </button>
        <div class="text-center text-[10px] text-[#9A857A] mt-3">
          Almacen Cori &bull; Beni
        </div>
      </div>
    </aside>
  </div>


  <!-- ═══════════════════════════════════════
       ADMIN — Sidebar fijo colapsable
  ════════════════════════════════════════ -->
  <aside
    v-else
    :class="[
      isCollapsed ? 'w-[80px]' : 'w-[260px]',
      'h-screen bg-gradient-to-b from-[#FFF9F6] to-[#FFE4D6] border-r-2 border-[#FFD0B8] flex flex-col justify-between shadow-[3px_0_20px_rgba(255,107,43,0.05)] overflow-y-auto overflow-x-hidden transition-all duration-300'
    ]"
  >
    <div>
      <!-- Logo -->
      <div class="bg-gradient-to-br from-[#FF6B2B] to-[#E85510] pt-2 pb-4 px-4 text-center rounded-b-[24px]">
        <div :class="['flex mb-2', isCollapsed ? 'justify-center' : 'justify-end']">
          <button
            @click="isCollapsed = !isCollapsed"
            class="p-1.5 rounded-lg bg-white/20 text-white hover:bg-white/30 transition-colors text-[10px] shadow-sm"
          >
            {{ isCollapsed ? '>>' : '<<' }}
          </button>
        </div>

        <img src="/src/assets/logo.png" alt="Logo"
          class="w-[180px] h-[180px] object-cover rounded-full mx-auto block mb-2 bg-white"
          @error="handleImageError" v-if="hasLogo"
        />
        <div v-else class="w-[100px] h-[100px] rounded-full mx-auto mb-2 bg-white flex items-center justify-center text-2xl">🛒</div>

        <h1 v-if="!isCollapsed" class="text-white font-black text-sm tracking-[0.1em] mt-2 uppercase">Almacen Cori</h1>
        <p v-if="!isCollapsed" class="text-[#FFE4D4] text-[10px] italic mt-1">Precio, calidad y confianza.</p>
      </div>

      <!-- Estado caja -->
      <div v-if="!isCollapsed">
        <div v-if="cajaStore.cajaAbierta"
          class="bg-white/60 border border-[#A5D6A7] border-l-[4px] border-l-[#4CAF50] rounded-xl py-2 px-3 mx-3 mt-4">
          <div class="text-[9px] uppercase tracking-wider text-gray-500 mb-1 flex items-center">
            <span class="w-2 h-2 rounded-full bg-[#4CAF50] mr-2"></span> Caja abierta
          </div>
          <div class="text-xs font-bold text-gray-800">Bs. {{ cajaStore.montoInicial.toFixed(2) }}</div>
          <div class="text-[10px] text-gray-600">Cajero: {{ cajaStore.cajero }}</div>
        </div>
        <div v-else
          class="bg-[#FFF3EE]/80 border border-[#FFCCB3] border-l-[4px] border-l-[#FF6B2B] rounded-xl py-2 px-3 mx-3 mt-4">
          <div class="text-[9px] uppercase tracking-wider text-gray-500 mb-1">Caja cerrada</div>
          <div class="text-xs font-bold text-gray-800">Abre para vender</div>
        </div>
      </div>
      <div v-else class="flex justify-center mt-4">
        <span :title="cajaStore.cajaAbierta ? 'Caja abierta' : 'Caja cerrada'">
          {{ cajaStore.cajaAbierta ? '🟢' : '🔴' }}
        </span>
      </div>

      <!-- Menú admin -->
      <div class="mt-5">
        <div v-if="!isCollapsed"
          class="text-[10px] font-extrabold tracking-[0.14em] uppercase text-[#A09088] px-5 mb-2">
          Menú
        </div>
        <nav class="flex flex-col gap-1 px-2">
          <router-link to="/" class="nav-link" active-class="nav-active" title="Dashboard">
            🏠 <span v-if="!isCollapsed">Dashboard</span>
          </router-link>
          <router-link to="/caja" class="nav-link" active-class="nav-active" title="Caja">
            💵 <span v-if="!isCollapsed">Control de Caja</span>
          </router-link>
          <router-link to="/inventario" class="nav-link" active-class="nav-active" title="Inventario">
            📦 <span v-if="!isCollapsed">Inventario</span>
          </router-link>
          <router-link to="/pos" class="nav-link" active-class="nav-active" title="POS">
            🛒 <span v-if="!isCollapsed">Punto de Venta</span>
          </router-link>
          <router-link to="/reportes" class="nav-link" active-class="nav-active" title="Reportes">
            📊 <span v-if="!isCollapsed">Reportes</span>
          </router-link>
          <router-link to="/proveedores" class="nav-link" active-class="nav-active" title="Proveedores">
            🏭 <span v-if="!isCollapsed">Proveedores</span>
          </router-link>
        </nav>
      </div>
    </div>

    <!-- Footer admin -->
    <div class="pb-4">
      <div v-if="!isCollapsed"
        class="bg-white/60 border border-[#FFD0B8] rounded-xl py-2 px-3 mx-3 mb-2">
        <div class="text-[9px] uppercase text-[#9A857A]">Ventas hoy</div>
        <div class="text-sm font-extrabold text-[#E85510]">Bs. {{ cajaStore.ventasTotalesHoy.toFixed(2) }}</div>
      </div>
      <div v-else class="text-center text-xl pb-2">📈</div>

      <button
        @click="handleLogout"
        class="flex items-center gap-2 mx-3 px-3 py-2 rounded-xl text-[11px] font-bold text-red-500 hover:bg-red-50 transition-colors w-[calc(100%-24px)]"
        :class="isCollapsed ? 'justify-center' : ''"
        title="Cerrar Sesión"
      >
        <span>🚪</span>
        <span v-if="!isCollapsed">Cerrar Sesión</span>
      </button>

      <div v-if="!isCollapsed" class="text-center text-[9px] text-[#9A857A] px-4">
        Almacen Cori &bull; Beni
      </div>
    </div>
  </aside>

</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useCajaStore } from '@/stores/cajaStore'

const router = useRouter()
const authStore = useAuthStore()
const cajaStore = useCajaStore()

const isCollapsed = ref(false)
const sidebarAbierto = ref(false)
const hasLogo = ref(true)
const handleImageError = () => { hasLogo.value = false }

const esAdmin = computed(() => authStore.user?.role === 'admin')

onMounted(async () => {
  if (esAdmin.value) {
    await cajaStore.cargarEstado()
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* Admin */
.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  color: #5C4A40;
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.7);
  color: #FF6B2B;
}
.nav-active {
  background: #FFFFFF !important;
  color: #E85510 !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
  font-weight: 700 !important;
}

/* Vendedor */
.nav-link-vendedor {
  display: flex;
  align-items: center;
  gap: 14px;
  border-radius: 16px;
  padding: 1rem 1.2rem;
  color: #5C4A40;
  text-decoration: none;
  transition: all 0.2s ease;
  background: white;
  border: 1px solid #FFE0CC;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.nav-link-vendedor:hover {
  background: #FFF3EE;
  border-color: #FF6B2B;
}
.nav-active-vendedor {
  background: #FFF3EE !important;
  border-color: #FF6B2B !important;
  color: #E85510 !important;
  box-shadow: 0 2px 8px rgba(255,107,43,0.15) !important;
}
</style>