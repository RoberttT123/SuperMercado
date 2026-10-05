<template>
  <div class="flex h-screen">
    <!-- Ocultar Sidebar en login -->
    <Sidebar v-if="mostrarSidebar" />

    <main
      class="flex-1 overflow-y-auto"
      :class="esVendedor && mostrarSidebar ? 'pt-10' : ''"
    >
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import Sidebar from '@/components/Sidebar.vue'

const route = useRoute()
const authStore = useAuthStore()

// Solo el vendedor usa el menú flotante (botón ☰ fijo arriba a la izquierda);
// el espacio extra es para que ese botón no tape el título. Admin y cajero
// tienen el menú lateral fijo y no lo necesitan.
const esVendedor = computed(() => authStore.user?.role === 'vendedor')

// Oculta el Sidebar únicamente en la página de login
const mostrarSidebar = computed(() => route.path !== '/login')
</script>