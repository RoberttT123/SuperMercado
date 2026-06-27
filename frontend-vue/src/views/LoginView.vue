<template>
  <!-- Fondo degradado naranja suave -->
  <div class="min-h-screen bg-gradient-to-br from-[#FFEDE0] to-[#FFD8B5] flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl shadow-[0_20px_50px_rgba(255,107,43,0.15)] w-full max-w-md p-8 border border-[#FFE0CC]">
      
      <div class="text-center mb-8">
        <!-- LOGO -->
        <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-[#FFF3EE] shadow-sm overflow-hidden">
          <img 
            v-if="hasLogo" 
            src="@/assets/logo.png" 
            alt="Logo Almacen" 
            @error="handleImageError"
            class="w-full h-full object-cover"
          />
          <span v-else class="text-4xl">🛒</span>
        </div>
        
        <h1 class="text-2xl font-black text-[#2A1A0A] uppercase tracking-wide">
          Almacen <span class="text-[#FF6B2B]">Gloria</span>
        </h1>
        <p class="text-sm text-gray-500 italic mt-1">Precio, calidad y confianza.</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">Usuario</label>
          <input 
            v-model="username" 
            type="text" 
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:border-[#FF6B2B] focus:ring-2 focus:ring-[#FF6B2B]/20 transition-colors"
            placeholder="admin"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">Contraseña</label>
          <input 
            v-model="password" 
            type="password" 
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:border-[#FF6B2B] focus:ring-2 focus:ring-[#FF6B2B]/20 transition-colors"
            placeholder="••••••••"
          />
        </div>

        <div v-if="errorMessage" class="text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-100 text-center">
          {{ errorMessage }}
        </div>

        <button 
          type="submit" 
          :disabled="isLoading"
          class="w-full bg-gradient-to-r from-[#FF6B2B] to-[#E85510] text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-[#FF6B2B]/20 hover:shadow-xl hover:opacity-90 transition-all disabled:opacity-50 mt-4 active:scale-[0.98]"
        >
          {{ isLoading ? 'Validando...' : 'Ingresar al Sistema' }}
        </button>
      </form>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/authService' // <-- Importa tu servicio

const router = useRouter()
const username = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const hasLogo = ref(true)

const handleImageError = () => { hasLogo.value = false }

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    // Llama al backend real a través de tu servicio
    await authService.login(username.value, password.value)
    
    // Si no lanza error, el authService ya guardó el token y el user en localStorage
    router.push('/')
  } catch (error) {
    // Muestra el mensaje de error que viene del backend o de Axios
    errorMessage.value = typeof error === 'string' ? error : 'Error al conectar con el servidor'
  } finally {
    isLoading.value = false
  }
}
</script>