<template>
  <aside class="w-64 h-screen bg-gradient-to-b from-[#FFF9F6] to-[#FFE4D6] border-r border-[#FFD0B8] flex flex-col shadow-[3px_0_20px_rgba(255,107,43,0.05)]">
    
    <div class="pt-8 pb-4 text-center">
      <div class="w-28 h-28 mx-auto mb-3 rounded-full border-2 border-white shadow-md overflow-hidden">
        <img src="@/assets/logo.png" class="w-full h-full object-cover" alt="Logo" />
      </div>
      <h1 class="text-[#E85510] font-black tracking-widest text-sm">ALMACEN GLORIA</h1>
      <p class="text-[10px] text-[#FF6B2B] italic mt-1">Precio, calidad y confianza</p>
    </div>

    <div class="mx-4 mt-2 mb-4 p-3 bg-white/60 border border-[#FFD0B8] rounded-xl backdrop-blur-sm">
      <div class="text-[10px] uppercase font-bold text-[#9A857A] mb-1 flex items-center">
        <span class="w-2 h-2 rounded-full bg-[#4CAF50] mr-2 animate-pulse"></span>
        Caja abierta
      </div>
      <div class="text-sm font-bold text-[#333]">Bs. 500.00 inicial</div>
      <div class="text-[10px] text-[#666] mt-1">Cajero: Admin</div>
    </div>

    <nav class="flex-1 px-3 space-y-1">
      <div class="text-[10px] font-bold text-[#A09088] uppercase tracking-widest px-3 mb-2 mt-4">Menu principal</div>
      
      <router-link to="/" class="flex items-center p-3 rounded-lg text-[#5C4A40] hover:bg-white/50 hover:text-[#FF6B2B] hover:border-[#FFCCB3] border border-transparent transition-all">
        🏠 Dashboard
      </router-link>
      <router-link to="/pos" class="flex items-center p-3 rounded-lg text-[#5C4A40] hover:bg-white/50 hover:text-[#FF6B2B] hover:border-[#FFCCB3] border border-transparent transition-all">
        🛒 Punto de Venta
      </router-link>
      
      <div v-if="userRole === 'admin'">
        <router-link to="/reportes" class="flex items-center p-3 rounded-lg text-[#5C4A40] hover:bg-white/50 hover:text-[#FF6B2B] hover:border-[#FFCCB3] border border-transparent transition-all">
          📊 Reportes
        </router-link>
      </div>
    </nav>

    <div class="p-4 text-center text-[10px] text-[#9A857A] border-t border-[#EAD5C9]">
      Almacen Gloria &bull; Beni, Bolivia
    </div>
  </aside>
</template>

<script setup>
// Asegúrate de que este import coincida con la ruta de tu store
import { userRole } from '@/lib/userStore' 
</script>

<style scoped>
/* Estilo para el link activo (cuando estás en la página) */
.router-link-active {
  background-color: white !important;
  color: #E85510 !important;
  border-color: #FFCCB3 !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 10px rgba(232,85,16,0.08) !important;
}
</style>