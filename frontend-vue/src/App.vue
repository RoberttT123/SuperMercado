<!-- App.vue o el layout principal -->
<template>
  <div class="flex h-screen">
    <Sidebar />
    <main
      class="flex-1 overflow-y-auto"
      :class="!esAdmin ? 'pt-16' : ''"
    >
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import Sidebar from '@/components/Sidebar.vue'

const authStore = useAuthStore()
const esAdmin = computed(() => authStore.user?.role === 'admin')
</script>