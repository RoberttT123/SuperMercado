<template>
  <div class="p-4 md:p-8 md:pl-10 max-w-full">
    <div class="mb-6 border-b border-[#FFE0CC] pb-4">
      <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">🕑 Historial de movimientos</h1>
      <p class="text-gray-500 text-sm">Quién agregó productos, cambió precios o movió stock, y cuándo. Solo lo ve el administrador.</p>
    </div>

    <!-- Filtros -->
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-[#FFE0CC] mb-6 flex flex-wrap gap-4 items-end">
      <div class="w-full sm:w-48">
        <label class="block text-sm font-bold text-gray-700 mb-1">📅 Período</label>
        <select v-model="periodo" @change="cargar" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          <option v-for="p in PERIODOS" :key="p" :value="p">{{ p }}</option>
        </select>
      </div>

      <template v-if="periodo === 'Rango personalizado'">
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-1">Desde</label>
          <input type="date" v-model="fechaDesde" @change="cargar" class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
        </div>
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-1">Hasta</label>
          <input type="date" v-model="fechaHasta" @change="cargar" class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
        </div>
      </template>

      <div class="w-full sm:w-56">
        <label class="block text-sm font-bold text-gray-700 mb-1">👤 Usuario</label>
        <select v-model="filtroUsuario" @change="cargar" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          <option value="">Todos</option>
          <option v-for="u in usuarios" :key="u.username" :value="u.username">{{ u.username }} ({{ u.role }})</option>
        </select>
      </div>

      <div class="w-full sm:w-52">
        <label class="block text-sm font-bold text-gray-700 mb-1">🔎 Tipo de movimiento</label>
        <select v-model="filtroTipo" @change="cargar" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          <option value="">Todos</option>
          <optgroup v-for="g in GRUPOS_TIPO" :key="g.grupo" :label="g.grupo">
            <option v-for="t in g.tipos" :key="t" :value="t">{{ TIPOS[t].texto }}</option>
          </optgroup>
        </select>
      </div>

      <div class="w-full md:w-auto md:ml-auto flex gap-3">
        <button @click="exportarExcel" :disabled="exportando || total === 0"
          class="flex-1 md:flex-none bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold py-2 px-6 rounded-lg transition-colors">
          {{ exportando ? '⏳ Generando...' : '📊 Exportar Excel' }}
        </button>
        <button @click="cargar" :disabled="cargando"
          class="flex-1 md:flex-none bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 font-bold py-2 px-6 rounded-lg transition-colors">
          {{ cargando ? '🔄 Cargando...' : '🔄 Actualizar' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm font-medium">
      {{ error }}
    </div>

    <!-- Resumen -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
      <div class="bg-white rounded-xl p-4 border border-[#FFE0CC] shadow-sm">
        <div class="text-xs md:text-sm font-bold text-gray-400 uppercase">🧾 Movimientos</div>
        <div class="text-3xl font-black text-[#FF6B2B] mt-1">{{ total }}</div>
      </div>
      <div class="bg-white rounded-xl p-4 border border-[#FFE0CC] shadow-sm">
        <div class="text-xs md:text-sm font-bold text-gray-400 uppercase">➕ Productos nuevos</div>
        <div class="text-3xl font-black text-[#FF6B2B] mt-1">{{ contar('producto_creado', 'nivel_agregado') }}</div>
      </div>
      <div class="bg-white rounded-xl p-4 border border-[#FFE0CC] shadow-sm">
        <div class="text-xs md:text-sm font-bold text-gray-400 uppercase">🏷️ Cambios de precio</div>
        <div class="text-3xl font-black text-[#FF6B2B] mt-1">{{ contar('precio_editado') }}</div>
      </div>
      <div class="bg-white rounded-xl p-4 border border-[#FFE0CC] shadow-sm">
        <div class="text-xs md:text-sm font-bold text-gray-400 uppercase">📦 Cambios de stock</div>
        <div class="text-3xl font-black text-[#FF6B2B] mt-1">{{ contar('stock_editado', 'stock_ajustado') }}</div>
      </div>
    </div>

    <!-- Por usuario: click para filtrar -->
    <div v-if="porUsuario.length" class="flex flex-wrap items-center gap-2 mb-6">
      <span class="text-sm font-bold text-gray-500 mr-1">Por usuario:</span>
      <button v-for="u in porUsuario" :key="u.usuario" @click="alternarUsuario(u.usuario)"
        :class="['text-xs font-bold px-3 py-1.5 rounded-full border transition-colors',
          filtroUsuario === u.usuario
            ? 'bg-[#FF6B2B] text-white border-[#FF6B2B]'
            : 'bg-white text-gray-700 border-[#FFD0B8] hover:border-[#FF6B2B]']">
        {{ u.usuario }} · {{ u.cantidad }}
      </button>
    </div>

    <!-- Tabla -->
    <div class="bg-white rounded-2xl border border-[#FFE0CC] shadow-sm p-4 md:p-6">
      <div class="flex flex-wrap justify-between items-baseline gap-2 mb-4">
        <h2 class="text-lg font-bold text-gray-700">📋 Detalle</h2>
        <span v-if="total > movimientos.length" class="text-xs text-gray-500">
          Se muestran los {{ movimientos.length }} más recientes de {{ total }}. Exporta a Excel para verlos todos.
        </span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-[760px] text-left border-collapse">
          <thead>
            <tr class="border-b-2 border-gray-100 text-sm text-gray-500 whitespace-nowrap">
              <th class="pb-2 pr-4">Fecha y hora</th>
              <th class="pb-2 pr-4">Usuario</th>
              <th class="pb-2 pr-4">Movimiento</th>
              <th class="pb-2 pr-4">Producto</th>
              <th class="pb-2">Detalle</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="cargando && movimientos.length === 0">
              <td colspan="5" class="py-8 text-center text-gray-400 text-sm">Cargando historial...</td>
            </tr>
            <tr v-else-if="movimientos.length === 0">
              <td colspan="5" class="py-8 text-center text-gray-400 text-sm">No hay movimientos con estos filtros.</td>
            </tr>
            <tr v-for="m in movimientos" :key="m.id" class="align-top hover:bg-orange-50 transition-colors">
              <td class="py-3 pr-4 text-sm whitespace-nowrap">
                <div class="font-bold text-gray-800">{{ formatoHora(m.fecha) }}</div>
                <div class="text-xs text-gray-500">{{ formatoFecha(m.fecha) }}</div>
              </td>
              <td class="py-3 pr-4 text-sm">
                <div class="font-semibold text-gray-800 whitespace-nowrap">{{ m.usuario }}</div>
                <div class="text-xs text-gray-500 capitalize">{{ m.rol || '—' }}</div>
              </td>
              <td class="py-3 pr-4">
                <span :class="['inline-block text-xs font-bold px-2 py-1 rounded-full border whitespace-nowrap', (TIPOS[m.accion] || TIPO_DESCONOCIDO).clase]">
                  {{ (TIPOS[m.accion] || TIPO_DESCONOCIDO).texto }}
                </span>
              </td>
              <td class="py-3 pr-4 text-sm">
                <div class="font-semibold text-gray-800">{{ m.producto_nombre || '—' }}</div>
                <div v-if="m.nivel" class="text-xs text-gray-500 capitalize">{{ m.nivel }}</div>
              </td>
              <td class="py-3 text-sm text-gray-600">{{ m.detalle }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p class="text-xs text-gray-400 mt-4">
        El historial registra los cambios desde que se activó este módulo; lo anterior no aparece.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import historialService from '@/services/historialService'

const PERIODOS = ['Hoy', 'Ayer', 'Últimos 7 días', 'Últimos 30 días', 'Este mes', 'Rango personalizado']

const TIPOS = {
  producto_creado:   { texto: 'Producto creado',   clase: 'bg-green-50 text-green-700 border-green-200' },
  nivel_agregado:    { texto: 'Nivel agregado',    clase: 'bg-green-50 text-green-700 border-green-200' },
  producto_editado:  { texto: 'Producto editado',  clase: 'bg-gray-100 text-gray-700 border-gray-200' },
  nivel_editado:     { texto: 'Nivel editado',     clase: 'bg-gray-100 text-gray-700 border-gray-200' },
  nivel_eliminado:   { texto: 'Nivel eliminado',   clase: 'bg-red-50 text-red-700 border-red-200' },
  precio_editado:    { texto: 'Cambio de precio',  clase: 'bg-amber-50 text-amber-700 border-amber-200' },
  stock_editado:     { texto: 'Cambio de stock',   clase: 'bg-blue-50 text-blue-700 border-blue-200' },
  stock_ajustado:    { texto: 'Ajuste de stock',   clase: 'bg-blue-50 text-blue-700 border-blue-200' },
  compra_registrada: { texto: 'Compra registrada', clase: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  venta_anulada:     { texto: 'Venta anulada',     clase: 'bg-red-50 text-red-700 border-red-200' },
}
const TIPO_DESCONOCIDO = { texto: 'Otro', clase: 'bg-gray-100 text-gray-700 border-gray-200' }

const GRUPOS_TIPO = [
  { grupo: 'Productos', tipos: ['producto_creado', 'nivel_agregado', 'producto_editado', 'nivel_editado', 'nivel_eliminado'] },
  { grupo: 'Precios', tipos: ['precio_editado'] },
  { grupo: 'Stock', tipos: ['stock_editado', 'stock_ajustado', 'compra_registrada'] },
  { grupo: 'Ventas', tipos: ['venta_anulada'] },
]

const periodo = ref('Últimos 7 días')
const fechaDesde = ref('')
const fechaHasta = ref('')
const filtroUsuario = ref('')
const filtroTipo = ref('')

const usuarios = ref([])
const movimientos = ref([])
const total = ref(0)
const porAccion = ref({})
const porUsuario = ref([])

const cargando = ref(false)
const exportando = ref(false)
const error = ref('')

// Fechas en hora local (Bolivia), no en UTC: después de las 20:00 toISOString() ya daría "mañana"
const pad = (n) => String(n).padStart(2, '0')
const fechaLocal = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

const aplicarPeriodo = () => {
  if (periodo.value === 'Rango personalizado') return
  const hoy = new Date()
  const desde = new Date(hoy)
  const hasta = new Date(hoy)
  if (periodo.value === 'Ayer') { desde.setDate(hoy.getDate() - 1); hasta.setDate(hoy.getDate() - 1) }
  if (periodo.value === 'Últimos 7 días') desde.setDate(hoy.getDate() - 6)
  if (periodo.value === 'Últimos 30 días') desde.setDate(hoy.getDate() - 29)
  if (periodo.value === 'Este mes') desde.setDate(1)
  fechaDesde.value = fechaLocal(desde)
  fechaHasta.value = fechaLocal(hasta)
}

const params = () => {
  const p = { inicio: fechaDesde.value, fin: fechaHasta.value }
  if (filtroUsuario.value) p.usuario = filtroUsuario.value
  if (filtroTipo.value) p.accion = filtroTipo.value
  return p
}

const cargar = async () => {
  aplicarPeriodo()
  if (!fechaDesde.value || !fechaHasta.value) return
  cargando.value = true
  error.value = ''
  try {
    const data = await historialService.listar(params())
    movimientos.value = data.movimientos
    total.value = data.total
    porAccion.value = data.por_accion
    porUsuario.value = data.por_usuario
  } catch (e) {
    error.value = '❌ ' + (e.response?.data?.detail || 'No se pudo cargar el historial')
  } finally {
    cargando.value = false
  }
}

const contar = (...tipos) => tipos.reduce((suma, t) => suma + (porAccion.value[t] || 0), 0)

const alternarUsuario = (usuario) => {
  filtroUsuario.value = filtroUsuario.value === usuario ? '' : usuario
  cargar()
}

const exportarExcel = async () => {
  exportando.value = true
  try {
    const blob = await historialService.descargarExcel(params())
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `Historial_${fechaDesde.value}_a_${fechaHasta.value}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    // Con responseType 'blob' el mensaje de error del backend también llega como blob
    let mensaje = e.message
    if (e.response?.data instanceof Blob) {
      try { mensaje = JSON.parse(await e.response.data.text()).detail || mensaje } catch { /* se queda el genérico */ }
    }
    alert('❌ No se pudo generar el Excel: ' + mensaje)
  } finally {
    exportando.value = false
  }
}

// Supabase manda microsegundos (6 decimales); se recortan a 3 para que todos los navegadores lo lean bien
const aFecha = (iso) => new Date(String(iso).replace(/(\.\d{3})\d+/, '$1'))
const formatoFecha = (iso) => aFecha(iso).toLocaleDateString('es-BO', { timeZone: 'America/La_Paz', day: '2-digit', month: '2-digit', year: 'numeric' })
const formatoHora = (iso) => aFecha(iso).toLocaleTimeString('es-BO', { timeZone: 'America/La_Paz', hour: '2-digit', minute: '2-digit' })

onMounted(async () => {
  cargar()
  try {
    usuarios.value = await historialService.getUsuarios()
  } catch {
    usuarios.value = []
  }
})
</script>
