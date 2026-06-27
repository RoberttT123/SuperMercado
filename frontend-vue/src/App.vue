<template>
  <div class="flex h-screen bg-[#FDF6F0]">
    <Sidebar v-if="!isLoginPage" />

    <main class="flex-1 overflow-y-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()

// Computed que detecta si estamos en la ruta de login
const isLoginPage = computed(() => route.path === '/login')
</script>