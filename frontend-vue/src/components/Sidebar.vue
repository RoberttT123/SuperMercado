<template>
  <aside 
    :class="[
      isCollapsed ? 'w-[80px]' : 'w-[260px]', 
      'h-screen bg-gradient-to-b from-[#FFF9F6] to-[#FFE4D6] border-r-2 border-[#FFD0B8] flex flex-col justify-between shadow-[3px_0_20px_rgba(255,107,43,0.05)] overflow-y-auto overflow-x-hidden transition-all duration-300'
    ]"
  >
    
    <div>
      <!-- BOTÓN TOGGLE -->
      

      <!-- LOGO Y TÍTULO -->
      <div class="bg-gradient-to-br from-[#FF6B2B] to-[#E85510] pt-2 pb-4 px-4 text-center rounded-b-[24px] relative">
        
        <div :class="['flex mb-2', isCollapsed ? 'justify-center' : 'justify-end']">
          <button @click="isCollapsed = !isCollapsed" class="p-1.5 rounded-lg bg-white/20 text-white hover:bg-white/30 transition-colors text-[10px] shadow-sm backdrop-blur-sm">
            {{ isCollapsed ? '>>' : '<<' }}
          </button>
        </div>

        <img src="/src/assets/logo.png" alt="Logo" class="w-[80px] h-[80px] object-cover rounded-full mx-auto block mb-2 bg-white" @error="handleImageError" v-if="hasLogo" />
        <div v-else class="w-[80px] h-[80px] rounded-full mx-auto mb-2 bg-white flex items-center justify-center text-2xl">🛒</div>
        
        <h1 v-if="!isCollapsed" class="text-white font-black text-sm tracking-[0.1em] mt-2 drop-shadow-sm uppercase">Almacen Gloria</h1>
        <p v-if="!isCollapsed" class="text-[#FFE4D4] text-[10px] italic mt-1">Precio, calidad y confianza.</p>
      </div>

      <!-- CAJA STATUS -->
      <div v-if="!isCollapsed">
        <div v-if="cajaAbierta" class="bg-white/60 border border-[#A5D6A7] border-l-[4px] border-l-[#4CAF50] rounded-xl py-2 px-3 mx-3 mt-4">
          <div class="text-[9px] uppercase tracking-wider text-gray-500 mb-1 flex items-center">
            <span class="w-2 h-2 rounded-full bg-[#4CAF50] mr-2"></span> Caja abierta
          </div>
          <div class="text-xs font-bold text-gray-800">Bs. {{ montoInicialCaja.toFixed(2) }}</div>
          <div class="text-[10px] text-gray-600">Cajero: {{ nombreCajero }}</div>
        </div>
        
        <div v-else class="bg-[#FFF3EE]/80 border border-[#FFCCB3] border-l-[4px] border-l-[#FF6B2B] rounded-xl py-2 px-3 mx-3 mt-4">
          <div class="text-[9px] uppercase tracking-wider text-gray-500 mb-1">Caja cerrada</div>
          <div class="text-xs font-bold text-gray-800">Abre para vender</div>
        </div>
      </div>
      
      <!-- MENÚ -->
      <div class="mt-5">
        <div v-if="!isCollapsed" class="text-[10px] font-extrabold tracking-[0.14em] uppercase text-[#A09088] px-5 mb-2">Menú</div>
        <nav class="flex flex-col gap-1 px-2">
          <router-link to="/" class="nav-link" active-class="nav-active" title="Inicio">🏠 <span v-if="!isCollapsed">Dashboard</span></router-link>
          <router-link to="/caja" class="nav-link" active-class="nav-active" title="Caja">💵 <span v-if="!isCollapsed">Control de Caja</span></router-link>
          <router-link to="/inventario" class="nav-link" active-class="nav-active" title="Inventario">📦 <span v-if="!isCollapsed">Inventario</span></router-link>
          <router-link to="/pos" class="nav-link" active-class="nav-active" title="POS">🛒 <span v-if="!isCollapsed">Punto de Venta</span></router-link>
          <router-link to="/reportes" class="nav-link" active-class="nav-active" title="Reportes">📊 <span v-if="!isCollapsed">Reportes</span></router-link>
        </nav>
      </div>
    </div>

    <!-- FOOTER -->
    <div class="pb-4">
      <div v-if="!isCollapsed" class="bg-white/60 border border-[#FFD0B8] rounded-xl py-2 px-3 mx-3 mb-2">
        <div class="text-[9px] uppercase text-[#9A857A]">Ventas hoy</div>
        <div class="text-sm font-extrabold text-[#E85510]">Bs. {{ ventasTotalesHoy.toFixed(2) }}</div>
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
      <div v-if="!isCollapsed" class="text-center text-[9px] text-[#9A857A] px-4">Almacen Gloria &bull; Beni</div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'      // 1. Importa useRouter
import { useAuthStore } from '@/stores/authStore' // 2. Importa el store
const router = useRouter()
const authStore = useAuthStore()
const isCollapsed = ref(false)
const hasLogo = ref(true)
const handleImageError = () => { hasLogo.value = false }

const cajaAbierta = ref(true)
const montoInicialCaja = ref(150.00)
const nombreCajero = ref('Admin')
const ventasTotalesHoy = ref(845.50)
const cantidadVentasHoy = ref(12)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  gap: 10px; /* Espaciado entre icono y texto */
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
  box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
  font-weight: 700 !important;
}

</style>
