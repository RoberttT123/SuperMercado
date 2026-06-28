<template>
  <div class="p-8 pl-10 max-w-full">
    <div class="mb-6 border-b border-[#FFE0CC] pb-4">
      <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">💵 Control de Caja</h1>
      <p class="text-gray-500 text-sm">Gestión de aperturas, cierres y arqueo de efectivo.</p>
    </div>

    <!-- Estado de caja -->
    <div v-if="cajaStore.cajaAbierta" class="bg-[#0a1f0a] border border-[#4CAF50] border-l-4 rounded-xl p-4 mb-6 text-white">
      ✅ <strong>Caja abierta</strong> desde {{ formatoFecha(cajaStore.cajaActiva?.fecha_apertura) }}
      &nbsp;|&nbsp; Monto inicial: <strong>Bs. {{ cajaStore.montoInicial.toFixed(2) }}</strong>
      &nbsp;|&nbsp; Cajero: <strong>{{ cajaStore.cajero }}</strong>
    </div>
    <div v-else class="bg-[#1f0a0a] border border-[#FF6B2B] border-l-4 rounded-xl p-4 mb-6 text-white">
      🔒 <strong>No hay caja abierta.</strong> Abre la caja para comenzar a vender.
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 mb-6">
      <button @click="activeTab = 'abrir'" :class="['px-6 py-3 font-bold text-sm', activeTab === 'abrir' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500']">🟢 Abrir Caja</button>
      <button @click="activeTab = 'cerrar'" :class="['px-6 py-3 font-bold text-sm', activeTab === 'cerrar' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500']">🔴 Cerrar Caja</button>
      <button @click="activeTab = 'historial'" :class="['px-6 py-3 font-bold text-sm', activeTab === 'historial' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500']">📋 Historial</button>
    </div>

    <div class="bg-white p-6 rounded-2xl shadow-sm border border-[#FFE0CC]">

      <!-- TAB: ABRIR -->
      <div v-if="activeTab === 'abrir'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Apertura de Caja</h2>
        <div v-if="cajaStore.cajaAbierta" class="text-gray-500 bg-gray-50 p-4 rounded-lg border border-gray-200">
          Ya hay una caja abierta. Ciérrala primero antes de abrir una nueva.
        </div>
        <div v-else class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold mb-1">Monto inicial (Bs.)</label>
            <input v-model.number="formApertura.monto" type="number" min="0" step="0.5"
              class="w-full p-2 border rounded-lg focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold mb-1">Nombre del cajero</label>
            <input v-model="formApertura.usuario" type="text"
              class="w-full p-2 border rounded-lg focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <button 
            @click="abrirCaja" 
            :disabled="cargando"
            class="col-span-2 bg-[#FF6B2B] text-white font-bold py-3 rounded-lg hover:bg-[#E85D04] disabled:opacity-50 transition-colors">
            {{ cargando ? '⏳ Abriendo...' : '🟢 Abrir Caja Ahora' }}
          </button>
        </div>
      </div>

      <!-- TAB: CERRAR -->
      <div v-if="activeTab === 'cerrar'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Cierre y Arqueo</h2>
        <div v-if="!cajaStore.cajaAbierta" class="text-gray-500 bg-gray-50 p-4 rounded-lg border border-gray-200">
          No hay caja abierta.
        </div>
        <div v-else>
          <!-- Resumen -->
          <div class="grid grid-cols-4 gap-4 mb-6">
            <div class="text-center p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div class="text-xs text-gray-500 mb-1">Transacciones</div>
              <div class="text-xl font-bold text-[#FF6B2B]">{{ resumen.total_transacciones }}</div>
            </div>
            <div class="text-center p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div class="text-xs text-gray-500 mb-1">Total Ventas</div>
              <div class="text-xl font-bold text-[#FF6B2B]">Bs. {{ resumen.total_ingresos.toFixed(2) }}</div>
            </div>
            <div class="text-center p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div class="text-xs text-gray-500 mb-1">Efectivo</div>
              <div class="text-xl font-bold text-[#FF6B2B]">Bs. {{ resumen.efectivo.toFixed(2) }}</div>
            </div>
            <div class="text-center p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div class="text-xs text-gray-500 mb-1">QR / Tarjeta</div>
              <div class="text-xl font-bold text-[#FF6B2B]">Bs. {{ (resumen.qr + resumen.tarjeta).toFixed(2) }}</div>
            </div>
          </div>

          <!-- Arqueo -->
          <div class="grid grid-cols-2 gap-6 mb-6">
            <div>
              <label class="block text-sm font-bold mb-1">Dinero contado en caja (Bs.)</label>
              <input v-model.number="montoContado" type="number" min="0" step="0.5"
                class="w-full p-2 border rounded-lg focus:outline-none focus:border-[#FF6B2B]">
              <p class="text-xs text-gray-400 mt-1">
                Esperado: Bs. {{ montoEsperado.toFixed(2) }} 
                (inicial Bs. {{ cajaStore.montoInicial.toFixed(2) }} + efectivo Bs. {{ resumen.efectivo.toFixed(2) }})
              </p>
            </div>
            <div>
              <label class="block text-sm font-bold mb-1">Notas del cierre</label>
              <input v-model="notasCierre" type="text" placeholder="Observaciones..."
                class="w-full p-2 border rounded-lg focus:outline-none focus:border-[#FF6B2B]">
            </div>
          </div>

          <!-- Diferencia -->
          <div class="flex items-center justify-between p-4 rounded-lg font-bold mb-6"
            :class="diferencia >= 0 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
            <span class="text-gray-700">Diferencia:</span>
            <span :class="diferencia >= 0 ? 'text-green-600' : 'text-red-600'" class="text-2xl">
              {{ diferencia >= 0 ? '+' : '' }}Bs. {{ diferencia.toFixed(2) }}
            </span>
          </div>

          <button 
            @click="cerrarCaja" 
            :disabled="cargando"
            class="w-full bg-[#FF6B2B] text-white font-bold py-3 rounded-lg hover:bg-[#E85D04] disabled:opacity-50 transition-colors">
            {{ cargando ? '⏳ Cerrando...' : '🔴 Cerrar Caja' }}
          </button>
        </div>
      </div>

      <!-- TAB: HISTORIAL -->
      <div v-if="activeTab === 'historial'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Historial de Cajas</h2>
        <div v-if="historial.length === 0" class="text-center text-gray-400 py-8 bg-gray-50 rounded-xl border border-gray-200">
          No hay cajas cerradas aún.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                <th class="pb-2">Apertura</th>
                <th class="pb-2">Cierre</th>
                <th class="pb-2">Cajero</th>
                <th class="pb-2 text-right">Monto Inicial</th>
                <th class="pb-2 text-right">Monto Final</th>
                <th class="pb-2 text-right">Diferencia</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="c in historial" :key="c.id" class="hover:bg-gray-50">
                <td class="py-3 text-sm">{{ formatoFecha(c.fecha_apertura) }}</td>
                <td class="py-3 text-sm">{{ formatoFecha(c.fecha_cierre) }}</td>
                <td class="py-3 text-sm">{{ c.usuario || '—' }}</td>
                <td class="py-3 text-right">Bs. {{ (c.monto_inicial || 0).toFixed(2) }}</td>
                <td class="py-3 text-right font-bold">Bs. {{ (c.monto_final || 0).toFixed(2) }}</td>
                <td class="py-3 text-right font-bold"
                  :class="(c.diferencia || 0) >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ (c.diferencia || 0) >= 0 ? '+' : '' }}Bs. {{ (c.diferencia || 0).toFixed(2) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useCajaStore } from '@/stores/cajaStore'
import cajaService from '@/services/cajaService'

const authStore = useAuthStore()
const cajaStore = useCajaStore()

const activeTab = ref('abrir')
const cargando = ref(false)

const resumen = ref({
  total_transacciones: 0,
  total_ingresos: 0,
  efectivo: 0,
  qr: 0,
  tarjeta: 0
})
const historial = ref([])

const formApertura = ref({
  monto: 100.0,
  usuario: authStore.user?.username || 'Cajero'
})
const montoContado = ref(0)
const notasCierre = ref('')

// --- COMPUTADOS ---
const montoEsperado = computed(() =>
  (cajaStore.montoInicial || 0) + (resumen.value?.efectivo || 0)
)
const diferencia = computed(() =>
  montoContado.value - montoEsperado.value
)

// --- CARGAR AL MONTAR ---
onMounted(async () => {
  await cajaStore.cargarEstado()
  if (cajaStore.cajaId) {
    resumen.value = await cajaService.getResumenCaja(cajaStore.cajaId)
    montoContado.value = montoEsperado.value
  }
  historial.value = await cajaService.getHistorial()
})

// --- ACCIONES ---
const abrirCaja = async () => {
  if (!formApertura.value.monto || !formApertura.value.usuario) {
    alert('⚠️ Completa el monto inicial y el nombre del cajero')
    return
  }
  cargando.value = true
  try {
    await cajaStore.abrir(formApertura.value.monto, formApertura.value.usuario)
    resumen.value = { total_transacciones: 0, total_ingresos: 0, efectivo: 0, qr: 0, tarjeta: 0 }
    alert(`✅ Caja abierta con Bs. ${formApertura.value.monto.toFixed(2)}`)
    activeTab.value = 'cerrar'
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error al abrir caja'))
  } finally {
    cargando.value = false
  }
}

const cerrarCaja = async () => {
  if (!confirm('¿Confirmas el cierre de caja?')) return
  cargando.value = true
  try {
    const resultado = await cajaStore.cerrar(montoContado.value, notasCierre.value)
    alert(
      `✅ Caja cerrada\n` +
      `Esperado: Bs. ${resultado.monto_esperado.toFixed(2)}\n` +
      `Contado:  Bs. ${resultado.monto_contado.toFixed(2)}\n` +
      `Diferencia: Bs. ${resultado.diferencia.toFixed(2)}`
    )
    resumen.value = { total_transacciones: 0, total_ingresos: 0, efectivo: 0, qr: 0, tarjeta: 0 }
    montoContado.value = 0
    notasCierre.value = ''
    historial.value = await cajaService.getHistorial()
    activeTab.value = 'historial'
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error al cerrar caja'))
  } finally {
    cargando.value = false
  }
}

// --- FORMATO ---
const formatoFecha = (f) => {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-BO', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>