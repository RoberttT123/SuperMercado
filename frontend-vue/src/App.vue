<template>
  <div class="flex min-h-screen bg-[#FDF6F0]">
    <Sidebar />
    
    <main class="flex-1 overflow-y-auto">
      <div class="p-8">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue'
</script>