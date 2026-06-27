<template>
  <div class="p-8 pl-10 max-w-full">
    <div class="mb-6 border-b border-[#FFE0CC] pb-4">
      <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">💵 Control de Caja</h1>
      <p class="text-gray-500 text-sm">Gestión de aperturas, cierres y arqueo de efectivo.</p>
    </div>

    <div v-if="cajaActiva" class="bg-[#0a1f0a] border border-[#4CAF50] border-l-4 rounded-xl p-4 mb-6 text-white">
      ✅ <strong>Caja abierta</strong> desde {{ formatoFecha(cajaActiva.fecha_apertura) }} 
      &nbsp;|&nbsp; Monto inicial: <strong>Bs. {{ cajaActiva.monto_inicial.toFixed(2) }}</strong>
      &nbsp;|&nbsp; Cajero: <strong>{{ cajaActiva.usuario }}</strong>
    </div>
    <div v-else class="bg-[#1f0a0a] border border-[#FF6B2B] border-l-4 rounded-xl p-4 mb-6 text-white">
      🔒 <strong>No hay caja abierta.</strong> Abre la caja para comenzar a vender.
    </div>

    <div class="flex border-b border-gray-200 mb-6">
      <button @click="activeTab = 'abrir'" :class="['px-6 py-3 font-bold text-sm', activeTab === 'abrir' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500']">🟢 Abrir Caja</button>
      <button @click="activeTab = 'cerrar'" :class="['px-6 py-3 font-bold text-sm', activeTab === 'cerrar' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500']">🔴 Cerrar Caja</button>
      <button @click="activeTab = 'historial'" :class="['px-6 py-3 font-bold text-sm', activeTab === 'historial' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500']">📋 Historial</button>
    </div>

    <div class="bg-white p-6 rounded-2xl shadow-sm border border-[#FFE0CC]">
      
      <div v-if="activeTab === 'abrir'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Apertura de Caja</h2>
        <div v-if="cajaActiva" class="text-gray-500">Ya hay una caja abierta.</div>
        <div v-else class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold mb-1">Monto inicial (Bs.)</label>
            <input v-model.number="formApertura.monto" type="number" class="w-full p-2 border rounded-lg">
          </div>
          <div>
            <label class="block text-sm font-bold mb-1">Nombre del cajero</label>
            <input v-model="formApertura.usuario" type="text" class="w-full p-2 border rounded-lg">
          </div>
          <button @click="abrirCaja" class="col-span-2 bg-[#FF6B2B] text-white font-bold py-2 rounded-lg hover:bg-[#E85D04]">🟢 Abrir Caja Ahora</button>
        </div>
      </div>

      <div v-if="activeTab === 'cerrar'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Cierre y Arqueo</h2>
        <div v-if="!cajaActiva" class="text-gray-500">No hay caja abierta.</div>
        <div v-else>
          <div class="grid grid-cols-4 gap-4 mb-6">
            <div class="text-center p-3 bg-gray-50 rounded-lg">
              <div class="text-xs text-gray-500">Transacciones</div>
              <div class="text-xl font-bold text-[#FF6B2B]">{{ resumen.total_transacciones }}</div>
            </div>
            <div class="text-center p-3 bg-gray-50 rounded-lg">
              <div class="text-xs text-gray-500">Total Ventas</div>
              <div class="text-xl font-bold text-[#FF6B2B]">Bs. {{ resumen.total_ingresos.toFixed(2) }}</div>
            </div>
            <div class="text-center p-3 bg-gray-50 rounded-lg">
              <div class="text-xs text-gray-500">Efectivo</div>
              <div class="text-xl font-bold text-[#FF6B2B]">Bs. {{ resumen.efectivo.toFixed(2) }}</div>
            </div>
            <div class="text-center p-3 bg-gray-50 rounded-lg">
              <div class="text-xs text-gray-500">QR / Tarjeta</div>
              <div class="text-xl font-bold text-[#FF6B2B]">Bs. {{ (resumen.qr + resumen.tarjeta).toFixed(2) }}</div>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-6 mb-6">
            <div>
              <label class="block text-sm font-bold mb-1">Dinero contado (Bs.)</label>
              <input v-model.number="montoContado" type="number" class="w-full p-2 border rounded-lg">
            </div>
            <div>
              <label class="block text-sm font-bold mb-1">Notas</label>
              <input v-model="notasCierre" type="text" class="w-full p-2 border rounded-lg">
            </div>
          </div>

          <div class="flex items-center justify-between p-4 bg-gray-100 rounded-lg font-bold mb-4">
            <span>Diferencia:</span>
            <span :class="diferencia >= 0 ? 'text-green-600' : 'text-red-600'" class="text-xl">Bs. {{ diferencia.toFixed(2) }}</span>
          </div>

          <button @click="cerrarCaja" class="w-full bg-[#FF6B2B] text-white font-bold py-3 rounded-lg hover:bg-[#E85D04]">🔴 Cerrar Caja</button>
        </div>
      </div>

      <div v-if="activeTab === 'historial'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Historial de Cajas</h2>
        <div v-for="c in historial" :key="c.id" class="border-b py-3">
          <div class="flex justify-between items-center">
            <span class="font-bold">{{ c.fecha_apertura }}</span>
            <span :class="c.diferencia >= 0 ? 'text-green-500' : 'text-red-500'">{{ c.diferencia >= 0 ? '✅' : '⚠️' }} Bs. {{ c.monto_final.toFixed(2) }}</span>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();
import { ref, computed } from 'vue'

const activeTab = ref('abrir')

// Datos simulados (Reemplazar con llamadas a tu API/Service)
const cajaActiva = ref({ id: 1, fecha_apertura: '2026-06-26 08:00', monto_inicial: 100.0, usuario: 'Admin' })
const resumen = ref({ total_transacciones: 12, total_ingresos: 550.0, efectivo: 300.0, qr: 250.0, tarjeta: 0.0 })
const historial = ref([
  { id: 1, fecha_apertura: '2026-06-25', monto_final: 800.0, diferencia: 0.0 }
])

const formApertura = ref({ monto: 100.0, usuario: 'Admin' })
const montoContado = ref(400.0)
const notasCierre = ref('')

const montoEsperado = computed(() => (cajaActiva.value?.monto_inicial || 0) + (resumen.value?.efectivo || 0))
const diferencia = computed(() => montoContado.value - montoEsperado.value)

const formatoFecha = (f) => f // Función auxiliar de formato
const abrirCaja = () => alert('Caja abierta')
const cerrarCaja = () => alert('Caja cerrada')
</script>