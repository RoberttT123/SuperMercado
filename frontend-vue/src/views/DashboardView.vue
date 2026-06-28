<template>
  <div class="p-8 pl-10 max-w-full">

    <!-- HERO BANNER -->
    <header class="bg-white rounded-2xl border-l-[6px] border-[#FF6B2B] p-8 mb-8 shadow-sm flex items-center justify-between">
      <div class="flex items-center gap-6">
        <div class="w-20 h-20 bg-[#FFF3EE] rounded-full flex items-center justify-center text-4xl border border-[#FFCCB3]">🛒</div>
        <div>
          <span class="inline-block bg-[#FFF3EE] text-[#E85510] px-3 py-1 rounded-full text-xs font-black tracking-widest uppercase border border-[#FFCCB3] mb-2">
            Sistema de Gestión Comercial
          </span>
          <h1 class="text-4xl font-black text-[#2A1A0A]">Almacen <span class="text-[#FF6B2B]">Gloria</span></h1>
          <p class="text-gray-500 italic mt-1">Precio, calidad y confianza.</p>
        </div>
      </div>
      <div class="text-right text-sm text-gray-400">
        <div class="font-bold text-gray-600">{{ fechaHoy }}</div>
        <div>{{ authStore.user?.username }}</div>
        <div class="mt-1">
          <span v-if="cajaStore.cajaAbierta" class="text-green-600 font-bold text-xs">🟢 Caja abierta</span>
          <span v-else class="text-red-500 font-bold text-xs">🔴 Caja cerrada</span>
        </div>
      </div>
    </header>

    <!-- LOADING -->
    <div v-if="cargando" class="text-center py-12 text-[#FF6B2B] font-bold">
      ⏳ Cargando datos del dashboard...
    </div>

    <div v-else>

      <!-- KPIs -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-2xl p-5 border border-[#FFE0CC] shadow-sm">
          <div class="text-xs font-bold text-gray-400 uppercase mb-1">💰 Ventas Hoy</div>
          <div class="text-3xl font-black text-[#FF6B2B]">Bs. {{ resumen.ventas_hoy.toFixed(2) }}</div>
          <div class="text-xs mt-1" :class="resumen.variacion_hoy >= 0 ? 'text-green-600' : 'text-red-500'">
            {{ resumen.variacion_hoy >= 0 ? '▲' : '▼' }} {{ Math.abs(resumen.variacion_hoy) }}% vs ayer
          </div>
          <div class="text-xs text-gray-400 mt-1">{{ resumen.transacciones_hoy }} transacciones</div>
        </div>

        <div class="bg-white rounded-2xl p-5 border border-[#FFE0CC] shadow-sm">
          <div class="text-xs font-bold text-gray-400 uppercase mb-1">📅 Ventas del Mes</div>
          <div class="text-3xl font-black text-[#FF6B2B]">Bs. {{ resumen.ventas_mes.toFixed(2) }}</div>
          <div class="text-xs text-gray-400 mt-1">{{ resumen.transacciones_mes }} transacciones</div>
        </div>

        <div class="bg-white rounded-2xl p-5 border border-[#FFE0CC] shadow-sm">
          <div class="text-xs font-bold text-gray-400 uppercase mb-1">🎯 Ganancia Neta Mes</div>
          <div class="text-3xl font-black text-green-600">Bs. {{ resumen.ganancia_neta_mes.toFixed(2) }}</div>
          <div class="text-xs text-gray-400 mt-1">
            Margen: {{ resumen.ventas_mes > 0 ? ((resumen.ganancia_neta_mes / resumen.ventas_mes) * 100).toFixed(1) : 0 }}%
          </div>
        </div>

        <div class="bg-white rounded-2xl p-5 border shadow-sm"
          :class="resumen.productos_criticos > 0 ? 'border-red-300 bg-red-50' : 'border-[#FFE0CC]'">
          <div class="text-xs font-bold uppercase mb-1"
            :class="resumen.productos_criticos > 0 ? 'text-red-400' : 'text-gray-400'">
            ⚠️ Stock Crítico
          </div>
          <div class="text-3xl font-black"
            :class="resumen.productos_criticos > 0 ? 'text-red-600' : 'text-gray-400'">
            {{ resumen.productos_criticos }}
          </div>
          <div class="text-xs mt-1"
            :class="resumen.productos_criticos > 0 ? 'text-red-500' : 'text-gray-400'">
            {{ resumen.productos_criticos > 0 ? 'productos necesitan reposición' : 'todo en orden ✅' }}
          </div>
        </div>
      </section>

      <!-- GRÁFICO + TOP PRODUCTOS -->
      <section class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">

        <!-- Gráfico últimos 7 días -->
        <div class="lg:col-span-2 bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm">
          <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">📈 Ventas — Últimos 7 días</h2>
          <div v-if="ventasSemana.length === 0" class="text-center py-8 text-gray-400">
            Sin datos de ventas esta semana.
          </div>
          <div v-else class="flex items-end gap-2 h-48 px-2">
            <div
              v-for="dia in ventasSemana"
              :key="dia.dia"
              class="flex-1 flex flex-col items-center gap-1"
            >
              <span class="text-xs font-bold text-[#FF6B2B]">
                {{ dia.total > 0 ? 'Bs.' + dia.total.toFixed(0) : '' }}
              </span>
              <div
                class="w-full rounded-t-lg transition-all duration-500"
                :class="dia.total > 0 ? 'bg-[#FF6B2B]' : 'bg-gray-100'"
                :style="{ height: maxVentaSemana > 0 ? `${(dia.total / maxVentaSemana) * 160}px` : '8px', minHeight: '8px' }"
              ></div>
              <span class="text-[10px] text-gray-500 text-center">{{ dia.dia }}</span>
              <span class="text-[10px] text-gray-400">{{ dia.cantidad }}v</span>
            </div>
          </div>
        </div>

        <!-- Top 5 productos -->
        <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm">
          <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">🏆 Top Productos del Mes</h2>
          <div v-if="topProductos.length === 0" class="text-center py-8 text-gray-400 text-sm">
            Sin ventas este mes aún.
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="(prod, index) in topProductos"
              :key="prod.nombre"
              class="flex items-center gap-3"
            >
              <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-black text-white flex-shrink-0"
                :class="index === 0 ? 'bg-yellow-400' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-amber-600' : 'bg-[#FFE0CC] text-[#FF6B2B]'">
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-bold text-gray-800 truncate">{{ prod.nombre }}</div>
                <div class="w-full bg-gray-100 rounded-full h-1.5 mt-1">
                  <div class="bg-[#FF6B2B] h-1.5 rounded-full"
                    :style="{ width: `${(prod.unidades / topProductos[0].unidades) * 100}%` }">
                  </div>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <div class="text-xs font-black text-[#FF6B2B]">{{ prod.unidades }} u.</div>
                <div class="text-[10px] text-gray-400">Bs. {{ prod.ingresos.toFixed(0) }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ÚLTIMAS VENTAS + STOCK CRÍTICO -->
      <section class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

        <!-- Últimas ventas -->
        <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-bold text-[#FF6B2B]">🧾 Últimas Ventas</h2>
            <router-link to="/reportes" class="text-xs text-[#FF6B2B] font-bold hover:underline">Ver todas →</router-link>
          </div>
          <div v-if="ultimasVentas.length === 0" class="text-center py-6 text-gray-400 text-sm">
            No hay ventas registradas aún.
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="venta in ultimasVentas"
              :key="venta.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100 hover:bg-orange-50 transition-colors"
            >
              <div>
                <div class="font-bold text-sm text-[#FF6B2B]">{{ venta.numero_venta }}</div>
                <div class="text-xs text-gray-400">{{ formatoFecha(venta.fecha) }}</div>
              </div>
              <div class="text-right">
                <div class="font-black text-gray-800">Bs. {{ venta.total.toFixed(2) }}</div>
                <div class="text-xs capitalize text-gray-400">{{ venta.metodo_pago }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Stock crítico -->
        <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-bold text-[#FF6B2B]">⚠️ Stock Crítico</h2>
            <router-link to="/inventario" class="text-xs text-[#FF6B2B] font-bold hover:underline">Ver inventario →</router-link>
          </div>
          <div v-if="stockCritico.length === 0" class="text-center py-6">
            <div class="text-3xl mb-2">✅</div>
            <div class="text-green-600 font-bold text-sm">Todo el stock está en orden</div>
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="prod in stockCritico"
              :key="prod.nombre"
              class="flex items-center justify-between p-3 bg-red-50 rounded-xl border border-red-100"
            >
              <div>
                <div class="font-bold text-sm text-gray-800">{{ prod.nombre }}</div>
                <div class="text-xs text-gray-400">{{ prod.categoria }}</div>
              </div>
              <div class="text-right">
                <div class="font-black text-red-600 text-lg">{{ prod.stock }}</div>
                <div class="text-xs text-gray-400">mín: {{ prod.stock_minimo }}</div>
                <div class="text-xs font-bold text-red-500">faltan {{ prod.faltante }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- MÓDULOS -->
      <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <article class="app-card">
          <h3 class="text-xl font-bold text-[#2A1A0A] mb-3">💵 Control de Caja</h3>
          <p class="text-sm text-gray-600 mb-6 leading-relaxed">Abre y cierra la caja del día. Realiza el arqueo y consulta el historial.</p>
          <router-link to="/caja" class="btn-primary">Ir a Caja</router-link>
        </article>
        <article class="app-card">
          <h3 class="text-xl font-bold text-[#2A1A0A] mb-3">📦 Inventario</h3>
          <p class="text-sm text-gray-600 mb-6 leading-relaxed">Registra productos, actualiza precios y gestiona el stock disponible.</p>
          <router-link to="/inventario" class="btn-primary">Ir a Inventario</router-link>
        </article>
        <article class="app-card">
          <h3 class="text-xl font-bold text-[#2A1A0A] mb-3">🛒 Punto de Venta</h3>
          <p class="text-sm text-gray-600 mb-6 leading-relaxed">Escanea códigos de barra, procesa ventas y cobra de forma rápida.</p>
          <router-link to="/pos" class="btn-primary">Ir a POS</router-link>
        </article>
        <article class="app-card">
          <h3 class="text-xl font-bold text-[#2A1A0A] mb-3">📊 Reportes</h3>
          <p class="text-sm text-gray-600 mb-6 leading-relaxed">Consulta gráficos de ventas, utilidades netas y artículos más vendidos.</p>
          <router-link to="/reportes" class="btn-primary">Ir a Reportes</router-link>
        </article>
      </section>

    </div>

    <footer class="mt-4 pt-8 border-t border-[#FFE0CC] text-center text-gray-400 text-sm">
      Panel Central · Almacen Gloria · Beni, Bolivia
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useCajaStore } from '@/stores/cajaStore'
import dashboardService from '@/services/dashboardService'

const authStore = useAuthStore()
const cajaStore = useCajaStore()

const cargando = ref(true)

const resumen = ref({
  ventas_hoy: 0,
  transacciones_hoy: 0,
  ventas_ayer: 0,
  variacion_hoy: 0,
  ventas_mes: 0,
  transacciones_mes: 0,
  ganancia_neta_mes: 0,
  productos_criticos: 0
})

const ventasSemana = ref([])
const topProductos = ref([])
const ultimasVentas = ref([])
const stockCritico = ref([])

const maxVentaSemana = computed(() =>
  Math.max(...ventasSemana.value.map(d => d.total), 1)
)

const fechaHoy = new Date().toLocaleDateString('es-BO', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
})

onMounted(async () => {
  cargando.value = true
  try {
    const [r, semana, top, ultimas, stock] = await Promise.all([
      dashboardService.getResumen(),
      dashboardService.getVentasSemana(),
      dashboardService.getTopProductos(),
      dashboardService.getUltimasVentas(),
      dashboardService.getStockCritico()
    ])
    resumen.value = r
    ventasSemana.value = semana
    topProductos.value = top
    ultimasVentas.value = ultimas
    stockCritico.value = stock

    await cajaStore.cargarEstado()
  } catch (e) {
    console.error('Error cargando dashboard:', e)
  } finally {
    cargando.value = false
  }
})

const formatoFecha = (f) => {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-BO', {
    day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>