<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50">
    <div class="p-8 bg-white rounded-2xl shadow-xl w-full max-w-sm border border-gray-100">
      <h1 class="text-3xl font-bold text-center mb-2 text-orange-600">Almacén Gloria</h1>
      <p class="text-center text-gray-500 mb-8">Inicia sesión para continuar</p>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input 
            v-model="email" 
            type="email" 
            required
            class="w-full p-3 border border-gray-300 rounded-lg mt-1 focus:ring-2 focus:ring-orange-500 outline-none"
            placeholder="correo@ejemplo.com"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Contraseña</label>
          <input 
            v-model="password" 
            type="password" 
            required
            class="w-full p-3 border border-gray-300 rounded-lg mt-1 focus:ring-2 focus:ring-orange-500 outline-none"
            placeholder="••••••••"
          />
        </div>

        <button 
          type="submit"
          :disabled="loading"
          class="w-full bg-orange-500 text-white p-3 rounded-lg font-bold hover:bg-orange-600 transition disabled:bg-gray-400 mt-2"
        >
          {{ loading ? 'Ingresando...' : 'Entrar al Sistema' }}
        </button>
      </form>

      <p v-if="errorMsg" class="mt-4 text-red-500 text-sm text-center bg-red-50 p-2 rounded">
        {{ errorMsg }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { supabase } from '../lib/supabaseClient'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')
const router = useRouter()

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  
  // 1. Intentar iniciar sesión
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value,
  })

  if (error) {
    errorMsg.value = "Error: " + error.message
    loading.value = false
    return
  }

  // 2. Si es exitoso, verificar el rol en tu tabla 'usuarios'
  const { data: profile, error: profileError } = await supabase
    .from('usuarios')
    .select('role')
    .eq('id', data.user.id)
    .single()

  if (profileError) {
    errorMsg.value = "No se pudo cargar tu perfil de usuario."
    loading.value = false
    return
  }

  // 3. Redirección según el rol
  console.log("Bienvenido, rol detectado:", profile.role)
  
  if (profile.role === 'admin') {
    router.push('/dashboard') // Cambia esto por tu ruta de admin
  } else {
    router.push('/pos') // Cambia esto por tu ruta de ventas
  }

  loading.value = false
}
if (profile) {
  setUserRole(profile.role) // <--- ESTO GUARDA EL ROL GLOBALMENTE
  
  if (profile.role === 'admin') {
    router.push('/dashboard')
  } else {
    router.push('/pos')
  }
}
</script>