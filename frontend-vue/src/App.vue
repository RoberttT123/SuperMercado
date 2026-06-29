<template>
  <div class="flex h-screen">
    <!-- Ocultar Sidebar en login -->
    <Sidebar v-if="mostrarSidebar" />

    <main
      class="flex-1 overflow-y-auto"
      :class="!esAdmin && mostrarSidebar ? 'pt-16' : ''"
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

const esAdmin = computed(() => authStore.user?.role === 'admin')

// Oculta el Sidebar únicamente en la página de login
const mostrarSidebar = computed(() => route.path !== '/login')
</script>