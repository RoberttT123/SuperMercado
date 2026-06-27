<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold">Panel de Administración</h1>
    
    <div v-if="userRole === 'admin'" class="mt-6 p-4 bg-yellow-100 border border-yellow-400 rounded">
      <h2 class="font-bold">Herramientas de Admin</h2>
      <button class="bg-red-600 text-white p-2 rounded">Borrar Base de Datos</button>
    </div>

    <p v-else class="text-gray-500">No tienes permisos de administrador.</p>
  </div>
</template>

<script setup>
import { userRole } from '../lib/userStore' // Importamos el estado reactivo
</script>