<template>
  <div class="p-8 pl-10 max-w-full">
    <div class="mb-6 flex justify-between items-end border-b border-[#FFE0CC] pb-4">
      <div>
        <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">📊 Reportes y Analítica</h1>
        <p class="text-gray-500 text-sm">Analítica de ventas, ganancias y productos más vendidos.</p>
      </div>
    </div>

    <div class="bg-white rounded-2xl p-4 shadow-sm border border-[#FFE0CC] mb-6 flex flex-wrap gap-4 items-end">
      <div class="w-64">
        <label class="block text-sm font-bold text-gray-700 mb-1">📅 Período</label>
        <select 
          v-model="periodo" 
          @change="manejarCambioPeriodo"
          class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]"
        >
          <option value="Hoy">Hoy</option>
          <option value="Ayer">Ayer</option>
          <option value="Últimos 7 días">Últimos 7 días</option>
          <option value="Últimos 30 días">Últimos 30 días</option>
          <option value="Este mes">Este mes</option>
          <option value="Rango personalizado">Rango personalizado</option>
        </select>
      </div>

      <div v-if="periodo === 'Rango personalizado'" class="flex gap-4">
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-1">Desde</label>
          <input type="date" v-model="fechaDesde" class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
        </div>
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-1">Hasta</label>
          <input type="date" v-model="fechaHasta" class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
        </div>
      </div>
      
      <button 
        @click="cargarDatosReportes"
        :disabled="cargando"
        class="bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 font-bold py-2 px-6 rounded-lg transition-colors ml-auto"
      >
        {{ cargando ? '🔄 Cargando...' : '🔄 Actualizar' }}
      </button>
    </div>

    <div v-if="cargando && ventas.length === 0" class="text-center py-12 text-gray-500 font-medium">
      Cargando información desde el servidor...
    </div>

    <div v-else>
      <h2 class="text-lg font-bold text-gray-700 mb-3">📈 Resumen del período</h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl p-4 border border-[#FFE0CC] shadow-sm">
          <div class="text-sm font-bold text-gray-400 uppercase">🧾 Transacciones</div>
          <div class="text-3xl font-black text-[#FF6B2B] mt-1">{{ kpis.transacciones }}</div>
        </div>
        <div class="bg-white rounded-xl p-4 border border-[#FFE0CC] shadow-sm">
          <div class="text-sm font-bold text-gray-400 uppercase">💰 Ingresos</div>
          <div class="text-3xl font-black text-[#FF6B2B] mt-1">Bs. {{ kpis.ingresos.toFixed(2) }}</div>
        </div>
        <div class="bg-white rounded-xl p-4 border border-[#FFE0CC] shadow-sm">
          <div class="text-sm font-bold text-gray-400 uppercase">🏷️ Descuentos</div>
          <div class="text-3xl font-black text-[#FF6B2B] mt-1">Bs. {{ kpis.descuentos.toFixed(2) }}</div>
        </div>
        <div class="bg-white rounded-xl p-4 border border-[#FFE0CC] shadow-sm">
          <div class="text-sm font-bold text-gray-400 uppercase">🎫 Ticket Promedio</div>
          <div class="text-3xl font-black text-[#FF6B2B] mt-1">Bs. {{ kpis.ticketPromedio.toFixed(2) }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-[#FFF9F6] border-2 border-[#FF6B2B] rounded-2xl p-6 shadow-sm flex flex-col justify-center items-center text-center">
          <div class="text-sm font-black text-[#E85510] uppercase tracking-widest mb-2">Ganancia Neta del Período</div>
          <div class="text-4xl font-black text-[#2A1A0A]">Bs. {{ kpis.gananciaNeta.toFixed(2) }}</div>
        </div>
        
        <div class="md:col-span-2 bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm">
          <h3 class="text-md font-bold text-gray-700 mb-4">💳 Ingresos por método de pago</h3>
          <div class="grid grid-cols-3 gap-4">
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div class="text-xs text-gray-500 font-bold uppercase mb-1">💵 Efectivo</div>
              <div class="text-xl font-bold text-gray-800">Bs. {{ kpis.pagos.efectivo.toFixed(2) }}</div>
            </div>
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div class="text-xs text-gray-500 font-bold uppercase mb-1">📱 QR / Transf.</div>
              <div class="text-xl font-bold text-gray-800">Bs. {{ kpis.pagos.qr.toFixed(2) }}</div>
            </div>
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div class="text-xs text-gray-500 font-bold uppercase mb-1">💳 Tarjeta</div>
              <div class="text-xl font-bold text-gray-800">Bs. {{ kpis.pagos.tarjeta.toFixed(2) }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-4 flex border-b border-gray-200">
        <button @click="activeTab = 'ventas'" :class="['py-3 px-6 font-bold text-sm transition-colors', activeTab === 'ventas' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
          📋 Historial de Ventas
        </button>
        <button @click="activeTab = 'top'" :class="['py-3 px-6 font-bold text-sm transition-colors', activeTab === 'top' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
          🏆 Top Productos
        </button>
        <button @click="activeTab = 'stock'" :class="['py-3 px-6 font-bold text-sm transition-colors', activeTab === 'stock' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
          ⚠️ Stock Crítico
        </button>
      </div>

      <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm mb-10">
        
        <div v-if="activeTab === 'ventas'">
          <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div class="lg:col-span-3 overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                    <th class="pb-2">Nº Venta</th>
                    <th class="pb-2">Fecha</th>
                    <th class="pb-2">Método</th>
                    <th class="pb-2">Descuento</th>
                    <th class="pb-2">Total</th>
                    <th class="pb-2">Estado</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-if="ventas.length === 0">
                    <td colspan="6" class="py-4 text-center text-gray-400 text-sm">No se encontraron ventas en este período.</td>
                  </tr>
                  <tr 
                    v-for="v in ventas" 
                    :key="v.id" 
                    @click="cargarDetalleVentaReal(v)" 
                    class="hover:bg-orange-50 cursor-pointer transition-colors" 
                    :class="{'bg-orange-50': ventaSeleccionada?.id === v.id}"
                  >
                    <td class="py-3 font-bold text-[#FF6B2B]">{{ v.numero_venta }}</td>
                    <td class="py-3 text-sm">{{ v.fecha }}</td>
                    <td class="py-3 text-sm capitalize">{{ v.metodo_pago }}</td>
                    <td class="py-3 text-sm">Bs. {{ (v.descuento || 0).toFixed(2) }}</td>
                    <td class="py-3 font-bold">Bs. {{ v.total.toFixed(2) }}</td>
                    <td class="py-3 text-sm">
                      <span v-if="v.estado === 'completada'" class="text-green-600 bg-green-50 px-2 py-1 rounded">✅ Completada</span>
                      <span v-else class="text-red-600 bg-red-50 px-2 py-1 rounded">❌ Anulada</span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <p class="text-xs text-gray-400 mt-2">{{ ventas.length }} venta(s) en el período.</p>
            </div>

            <div class="lg:col-span-1 bg-gray-50 p-4 rounded-xl border border-gray-200 h-fit">
              <h3 class="font-bold text-gray-700 mb-4">Acciones</h3>
              
              <div v-if="!ventaSeleccionada" class="text-sm text-gray-500 text-center py-8">
                Haz clic en una venta de la tabla para ver sus detalles.
              </div>
              
              <div v-else>
                <div class="text-sm font-bold mb-2">Venta: {{ ventaSeleccionada.numero_venta }}</div>
                <div class="text-xs text-gray-600 mb-4">Cliente: {{ ventaSeleccionada.cliente || 'Consumidor final' }}</div>
                
                <div class="space-y-2 mb-4 max-h-60 overflow-y-auto">
                  <div v-for="(item, idx) in ventaSeleccionada.items" :key="idx" class="bg-white p-2 border border-gray-200 rounded text-xs flex justify-between">
                    <div>
                      <span class="font-bold">{{ item.cantidad }}x</span> {{ item.nombre }}
                    </div>
                    <div class="font-bold">Bs. {{ (item.cantidad * item.precio).toFixed(2) }}</div>
                  </div>
                </div>
                
                <button 
                  @click="descargarFacturaPDF(ventaSeleccionada.id)"
                  class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-2 rounded-lg transition-colors text-sm flex items-center justify-center gap-2"
                >
                  📥 Descargar PDF
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'top'">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                  <th class="pb-2">Código</th>
                  <th class="pb-2">Producto</th>
                  <th class="pb-2 text-center">Unidades</th>
                  <th class="pb-2 text-right">Ingresos</th>
                  <th class="pb-2 text-right">Ganancia</th>
                  <th class="pb-2 w-1/3 pl-4">Proporción (Unidades)</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-if="topProductos.length === 0">
                  <td colspan="6" class="py-4 text-center text-gray-400 text-sm">No hay registros de productos vendidos en este período.</td>
                </tr>
                <tr v-for="p in topProductos" :key="p.codigo" class="hover:bg-gray-50">
                  <td class="py-3 text-sm text-gray-500">{{ p.codigo }}</td>
                  <td class="py-3 font-medium">{{ p.nombre }}</td>
                  <td class="py-3 text-center font-bold">{{ p.unidades }}</td>
                  <td class="py-3 text-right">Bs. {{ p.ingresos.toFixed(2) }}</td>
                  <td class="py-3 text-right font-bold text-green-600">Bs. {{ p.ganancia.toFixed(2) }}</td>
                  <td class="py-3 pl-4">
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                      <div class="bg-[#FF6B2B] h-2.5 rounded-full" :style="{ width: `${(p.unidades / maxUnidades) * 100}%` }"></div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="activeTab === 'stock'">
          <div v-if="stockCritico.length === 0" class="bg-green-50 text-green-700 p-4 rounded-lg font-bold text-center border border-green-200">
            ✅ Todos los productos tienen stock suficiente.
          </div>
          
          <div v-else>
            <div class="bg-red-50 text-red-700 p-3 rounded-lg font-bold mb-4 border border-red-200 text-sm">
              ⚠️ {{ stockCritico.length }} producto(s) necesitan reposición urgente.
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                    <th class="pb-2">Código</th>
                    <th class="pb-2">Nombre</th>
                    <th class="pb-2">Categoría</th>
                    <th class="pb-2 text-center">Stock Actual</th>
                    <th class="pb-2 text-center">Mínimo</th>
                    <th class="pb-2 text-center">Faltante</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="s in stockCritico" :key="s.codigo" class="hover:bg-red-50/50">
                    <td class="py-3 text-sm text-gray-500">{{ s.codigo }}</td>
                    <td class="py-3 font-medium">{{ s.nombre }}</td>
                    <td class="py-3 text-sm">{{ s.categoria }}</td>
                    <td class="py-3 text-center font-black text-red-600">{{ s.stock }}</td>
                    <td class="py-3 text-center text-gray-500">{{ s.minimo }}</td>
                    <td class="py-3 text-center font-bold text-orange-600">{{ s.faltante }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import reportesService from '@/services/reportesService'
import ventasService from '@/services/ventasService'
import api from '@/services/api'

const authStore = useAuthStore()

const periodo = ref('Hoy')
const fechaDesde = ref('')
const fechaHasta = ref('')
const activeTab = ref('ventas')
const ventaSeleccionada = ref(null)
const cargando = ref(false)

const kpis = ref({
  transacciones: 0,
  ingresos: 0,
  descuentos: 0,
  ticketPromedio: 0,
  gananciaNeta: 0,
  pagos: { efectivo: 0, qr: 0, tarjeta: 0 }
})

const ventas = ref([])
const topProductos = ref([])
const stockCritico = ref([])

const formatearFecha = (fecha) => {
  return fecha.toISOString().split('T')[0]
}

const calcularFechasPorPeriodo = () => {
  const hoy = new Date()
  let desde = new Date()
  let hasta = new Date()

  switch (periodo.value) {
    case 'Hoy':
      break
    case 'Ayer':
      desde.setDate(hoy.getDate() - 1)
      hasta.setDate(hoy.getDate() - 1)
      break
    case 'Últimos 7 días':
      desde.setDate(hoy.getDate() - 7)
      break
    case 'Últimos 30 días':
      desde.setDate(hoy.getDate() - 30)
      break
    case 'Este mes':
      desde = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
      break
    case 'Rango personalizado':
      return { 
        inicio: fechaDesde.value, 
        fin: fechaHasta.value 
      }
  }

  fechaDesde.value = formatearFecha(desde)
  fechaHasta.value = formatearFecha(hasta)

  return { inicio: fechaDesde.value, fin: fechaHasta.value }
}

const manejarCambioPeriodo = () => {
  if (periodo.value !== 'Rango personalizado') {
    cargarDatosReportes()
  }
}

const cargarDatosReportes = async () => {
  cargando.value = true
  ventaSeleccionada.value = null
  
  const { inicio, fin } = calcularFechasPorPeriodo()

  try {
    const [resumenVentas, listaVentas, productosMasVendidos, reporteStock, rentabilidad] = await Promise.all([
      ventasService.getResumenVentas(inicio, fin),
      ventasService.getVentasPorRango(inicio, fin),
      ventasService.getProductosMasVendidos(inicio, fin),
      reportesService.getStockCriticoReporte(),
      reportesService.getReporteRentabilidad(inicio, fin).catch(() => ({ ganancia_neta: 0 }))
    ])

    kpis.value = {
      transacciones: resumenVentas.total_transacciones || 0,
      ingresos: resumenVentas.ingresos_totales || 0,
      descuentos: resumenVentas.descuentos || 0,
      ticketPromedio: resumenVentas.ticket_promedio || 0,
      gananciaNeta: rentabilidad.ganancia_neta || 0,
      pagos: {
        efectivo: resumenVentas.efectivo || 0,
        qr: resumenVentas.qr || 0,
        tarjeta: resumenVentas.tarjeta || 0
      }
    }

    ventas.value = listaVentas
    topProductos.value = productosMasVendidos
    stockCritico.value = reporteStock

  } catch (error) {
    console.error("Error al conectar con la API de Reportes:", error)
  } finally {
    cargando.value = false
  }
}

const cargarDetalleVentaReal = async (venta) => {
  try {
    const itemsDetalle = await ventasService.getDetalleVenta(venta.id)
    ventaSeleccionada.value = {
      ...venta,
      items: itemsDetalle
    }
  } catch (error) {
    console.error("Error al consultar el detalle de venta:", error)
  }
}

const descargarFacturaPDF = async (ventaId) => {
  try {
    const response = await api.get(`/ventas/${ventaId}/pdf`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `Factura_Venta_${ventaId}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error("No se pudo generar o descargar el documento PDF", error)
  }
}

onMounted(() => {
  cargarDatosReportes()
})

const maxUnidades = computed(() => {
  if (topProductos.value.length === 0) return 1
  return Math.max(...topProductos.value.map(p => p.unidades))
})
</script>