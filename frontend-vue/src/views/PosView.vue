<template>
  <div class="p-8 pl-10 max-w-full">
    <!-- Header -->
    <div class="mb-6 flex justify-between items-end border-b border-[#FFE0CC] pb-4">
      <div>
        <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">🛒 Punto de Venta</h1>
        <p class="text-gray-500 text-sm">Caja #1 · Cajero: {{ cajeroActual }}</p>
      </div>
      <div v-if="!cajaActiva" class="bg-red-100 text-red-700 px-4 py-2 rounded-lg font-bold border border-red-200">
        🔒 No hay caja abierta. Ve a Control de Caja.
      </div>
    </div>

    <!-- Layout Principal: Izquierda (3) / Derecha (2) -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6" v-if="cajaActiva">
      
      <!-- ================= COLUMNA IZQUIERDA ================= -->
      <div class="lg:col-span-3 flex flex-col gap-6">
        
        <!-- Búsqueda / Escaneo -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-[#FFE0CC]">
          <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">📊 Escanear o Buscar Producto</h2>
          
          <!-- Tabs de método -->
          <div class="flex gap-4 mb-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="metodoBusqueda" value="codigo" class="text-[#FF6B2B] focus:ring-[#FF6B2B]" />
              <span class="text-sm font-medium">Código de barras (escaneo)</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="metodoBusqueda" value="nombre" class="text-[#FF6B2B] focus:ring-[#FF6B2B]" />
              <span class="text-sm font-medium">Búsqueda por nombre</span>
            </label>
          </div>

          <!-- Input Código -->
          <div v-if="metodoBusqueda === 'codigo'" class="flex gap-3">
            <input type="text" v-model="codigoInput" @keyup.enter="simularBusqueda" placeholder="Escanea o escribe el código..." class="flex-1 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] focus:ring-2 focus:ring-[#FF6B2B]/20" autofocus />
            <input type="number" v-model.number="cantidadScan" min="1" class="w-24 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" />
            <button @click="simularBusqueda" class="bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-2 px-6 rounded-lg transition-colors flex items-center gap-2">
              ➕ Agregar
            </button>
          </div>

          <!-- Input Nombre (Simulado) -->
          <div v-if="metodoBusqueda === 'nombre'" class="flex gap-3">
            <input type="text" v-model="nombreBusq" placeholder="Ej: leche..." class="flex-1 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] focus:ring-2 focus:ring-[#FF6B2B]/20" />
            <input type="number" v-model.number="cantidadNom" min="1" class="w-24 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" />
            <button @click="simularBusqueda" class="bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-2 px-6 rounded-lg transition-colors flex items-center gap-2">
              ➕ Agregar
            </button>
          </div>
        </div>
        <!-- Resultados de búsqueda por nombre -->
        <div v-if="errorBusqueda" class="mt-2 p-3 bg-red-50 text-red-600 rounded-lg text-sm border border-red-200">
          {{ errorBusqueda }}
        </div>

        <div v-if="resultadosBusqueda.length > 0" class="mt-2 border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <div
            v-for="prod in resultadosBusqueda"
            :key="prod.id"
            @click="agregarAlCarrito(prod, cantidadNom)"
            class="flex justify-between items-center p-3 hover:bg-orange-50 cursor-pointer border-b border-gray-100 last:border-0 transition-colors"
          >
            <div>
              <span class="font-bold text-sm">{{ prod.nombre }}</span>
              <span class="text-xs text-gray-400 ml-2">{{ prod.codigo }}</span>
            </div>
            <div class="text-right">
              <span class="font-black text-[#FF6B2B]">Bs. {{ prod.precio_venta.toFixed(2) }}</span>
              <span class="text-xs text-gray-400 ml-2">Stock: {{ prod.stock }}</span>
            </div>
          </div>
        </div>

        <div v-if="buscando" class="mt-2 text-center text-sm text-gray-500">
          🔍 Buscando...
        </div>
        <!-- Carrito -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-[#FFE0CC] flex-1">
          <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">🛒 Carrito ({{ carrito.length }} items)</h2>
          
          <div v-if="carrito.length === 0" class="bg-orange-50 text-[#E85510] p-4 rounded-lg text-center border border-orange-100">
            El carrito está vacío. Escanea un producto para comenzar.
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="border-b-2 border-[#FFE0CC] text-sm text-gray-500">
                  <th class="pb-2">Producto</th>
                  <th class="pb-2 w-24">Cant.</th>
                  <th class="pb-2">Precio</th>
                  <th class="pb-2">Subtotal</th>
                  <th class="pb-2 text-center">—</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="(item, index) in carrito" :key="index" class="hover:bg-gray-50">
                  <td class="py-3 font-medium">{{ item.nombre }}</td>
                  <td class="py-3">
                    <input type="number" v-model.number="item.cantidad" @input="recalcularSubtotal(item)" min="1" class="w-16 p-1 border rounded text-center focus:outline-none focus:border-[#FF6B2B]" />
                  </td>
                  <td class="py-3">Bs. {{ item.precio_unitario.toFixed(2) }}</td>
                  <td class="py-3 font-bold text-[#2A1A0A]">Bs. {{ item.subtotal.toFixed(2) }}</td>
                  <td class="py-3 text-center">
                    <button @click="eliminarDelCarrito(index)" class="text-red-500 hover:text-red-700 bg-red-50 p-2 rounded hover:bg-red-100 transition-colors">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ================= COLUMNA DERECHA ================= -->
      <div class="lg:col-span-2 flex flex-col gap-6">
        
        <!-- Panel de Cobro -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-[#FFE0CC] flex flex-col gap-4">
          
          <!-- Descuento -->
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">🏷️ Descuento (Bs.)</label>
            <input type="number" v-model.number="descuento" min="0" :max="subtotal" step="0.5" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" />
          </div>

          <!-- Total a Pagar -->
          <div class="bg-[#FFF9F6] border-2 border-[#FF6B2B] rounded-xl p-4 text-center mt-2">
            <div class="text-sm font-black text-[#E85510] uppercase tracking-widest mb-1">Total a Pagar</div>
            <div class="text-4xl font-black text-[#2A1A0A]">Bs. {{ total.toFixed(2) }}</div>
          </div>

          <hr class="border-gray-200" />

          <!-- Método de pago -->
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">💳 Método de pago:</label>
            <div class="grid grid-cols-3 gap-2">
              <button @click="metodoPago = 'efectivo'" :class="['py-2 px-1 text-sm font-bold rounded-lg border transition-colors', metodoPago === 'efectivo' ? 'bg-[#FF6B2B] text-white border-[#FF6B2B]' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50']">💵 Efectivo</button>
              <button @click="metodoPago = 'qr'" :class="['py-2 px-1 text-sm font-bold rounded-lg border transition-colors', metodoPago === 'qr' ? 'bg-[#FF6B2B] text-white border-[#FF6B2B]' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50']">📱 QR</button>
              <button @click="metodoPago = 'tarjeta'" :class="['py-2 px-1 text-sm font-bold rounded-lg border transition-colors', metodoPago === 'tarjeta' ? 'bg-[#FF6B2B] text-white border-[#FF6B2B]' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50']">💳 Tarjeta</button>
            </div>
          </div>

          <!-- Monto recibido (Solo si es efectivo) -->
          <div v-if="metodoPago === 'efectivo'" class="bg-gray-50 p-4 rounded-xl border border-gray-200">
            <label class="block text-sm font-bold text-gray-700 mb-1">💵 Monto recibido (Bs.)</label>
            <input type="number" v-model.number="montoRecibido" min="0" class="w-full px-4 py-2 mb-3 rounded-lg border border-gray-300 focus:outline-none focus:border-[#FF6B2B]" />
            
            <div class="flex justify-between items-center text-lg">
              <span class="font-bold text-gray-600">Cambio:</span>
              <span :class="['font-black text-2xl', cambio >= 0 ? 'text-green-600' : 'text-red-500']">
                Bs. {{ cambio.toFixed(2) }}
              </span>
            </div>
          </div>

          <!-- Notas -->
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📝 Notas (opcional)</label>
            <input type="text" v-model="notasVenta" placeholder="Detalles de la venta..." class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" />
          </div>

          <!-- Botones de Acción -->
          <div class="grid grid-cols-2 gap-3 mt-4">
            <button @click="procesarVenta" :disabled="!puedeCobrar" :class="['py-3 rounded-xl font-black text-lg transition-all', puedeCobrar ? 'bg-[#4CAF50] hover:bg-[#43A047] text-white shadow-md' : 'bg-gray-200 text-gray-400 cursor-not-allowed']">
              ✅ COBRAR
            </button>
            <button @click="cancelarVenta" class="py-3 rounded-xl font-bold text-lg border-2 border-gray-200 text-gray-600 hover:bg-gray-50 transition-all">
              🗑️ Cancelar
            </button>
          </div>

          <!-- Mensaje Éxito -->
          <div v-if="ventaOk" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-xl text-center">
            <div class="text-green-600 text-3xl mb-2">✅</div>
            <h3 class="font-black text-green-800">¡Venta completada!</h3>
            <p class="text-sm text-green-700 mt-1">Nº {{ ventaOk.numero }} · Total: <strong>Bs. {{ ventaOk.total.toFixed(2) }}</strong></p>
            <button @click="ventaOk = null" class="mt-3 bg-white text-green-700 text-sm font-bold py-1 px-4 rounded border border-green-300 hover:bg-green-100">🔄 Nueva venta</button>
          </div>
        </div>

        <!-- Resumen del día -->
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-[#FFE0CC] flex justify-between items-center">
          <div>
            <p class="text-xs font-bold text-gray-400 uppercase">Ventas Hoy</p>
            <p class="text-xl font-black text-[#2A1A0A]">{{ ventasHoyCount }}</p>
          </div>
          <div class="text-right">
            <p class="text-xs font-bold text-gray-400 uppercase">Total Hoy</p>
            <p class="text-xl font-black text-[#FF6B2B]">Bs. {{ totalHoyMonto.toFixed(2) }}</p>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import posService from '@/services/posService'

const authStore = useAuthStore()

// --- ESTADO GLOBAL ---
const cajaActiva = ref(true)
const cajeroActual = ref(authStore.user?.username || 'Cajero')
const ventasHoyCount = ref(0)
const totalHoyMonto = ref(0)

// --- ESTADO DEL POS ---
const metodoBusqueda = ref('codigo')
const codigoInput = ref('')
const cantidadScan = ref(1)
const nombreBusq = ref('')
const cantidadNom = ref(1)
const resultadosBusqueda = ref([])
const buscando = ref(false)
const errorBusqueda = ref('')

const carrito = ref([])
const descuento = ref(0)
const metodoPago = ref('efectivo')
const montoRecibido = ref(0)
const notasVenta = ref('')
const ventaOk = ref(null)
const procesando = ref(false)

// --- COMPUTADOS ---
const subtotal = computed(() =>
  carrito.value.reduce((acc, item) => acc + item.subtotal, 0)
)

const total = computed(() =>
  Math.max(0, subtotal.value - (descuento.value || 0))
)

const cambio = computed(() => {
  if (metodoPago.value !== 'efectivo') return 0
  return (montoRecibido.value || 0) - total.value
})

const puedeCobrar = computed(() => {
  if (carrito.value.length === 0) return false
  if (procesando.value) return false
  if (metodoPago.value === 'efectivo' && (montoRecibido.value || 0) < total.value) return false
  return true
})

watch(total, (newTotal) => {
  if (metodoPago.value === 'efectivo' && carrito.value.length > 0) {
    montoRecibido.value = newTotal
  }
})

// --- CARGAR RESUMEN DEL DÍA ---
onMounted(async () => {
  await cargarResumenHoy()
})

const cargarResumenHoy = async () => {
  try {
    const resumen = await posService.getResumenHoy()
    ventasHoyCount.value = resumen.total_transacciones || 0
    totalHoyMonto.value = resumen.ingresos_totales || 0
  } catch (e) {
    console.error('Error cargando resumen:', e)
  }
}

// --- BÚSQUEDA DE PRODUCTOS ---
const simularBusqueda = async () => {
  const term = metodoBusqueda.value === 'codigo' ? codigoInput.value : nombreBusq.value
  if (!term) return

  buscando.value = true
  errorBusqueda.value = ''
  resultadosBusqueda.value = []

  try {
    let resultados = []

    if (metodoBusqueda.value === 'codigo') {
      resultados = await posService.buscarPorCodigo(term)
      if (resultados.length === 1) {
        // Código exacto → agregar directo al carrito
        agregarAlCarrito(resultados[0], cantidadScan.value)
        codigoInput.value = ''
        cantidadScan.value = 1
        return
      }
    } else {
      resultados = await posService.buscarPorNombre(term)
    }

    if (resultados.length === 0) {
      errorBusqueda.value = `No se encontró ningún producto con "${term}"`
    } else {
      resultadosBusqueda.value = resultados
    }
  } catch (e) {
    errorBusqueda.value = 'Error al buscar producto'
    console.error(e)
  } finally {
    buscando.value = false
  }
}

const agregarAlCarrito = (producto, cantidad = 1) => {
  if (producto.stock <= 0) {
    alert(`⚠️ "${producto.nombre}" no tiene stock disponible`)
    return
  }

  const index = carrito.value.findIndex(i => i.producto_id === producto.id)

  if (index !== -1) {
    const nuevaCantidad = carrito.value[index].cantidad + cantidad
    if (nuevaCantidad > producto.stock) {
      alert(`⚠️ Stock insuficiente. Disponible: ${producto.stock}`)
      return
    }
    carrito.value[index].cantidad = nuevaCantidad
    recalcularSubtotal(carrito.value[index])
  } else {
    carrito.value.push({
      producto_id: producto.id,
      codigo: producto.codigo,
      nombre: producto.nombre,
      precio_unitario: producto.precio_venta,
      precio_compra: producto.precio_compra,
      stock_disponible: producto.stock,
      cantidad: cantidad,
      subtotal: producto.precio_venta * cantidad
    })
  }

  // Limpiar búsqueda
  resultadosBusqueda.value = []
  nombreBusq.value = ''
  cantidadNom.value = 1
}

const recalcularSubtotal = (item) => {
  if (item.cantidad < 1) item.cantidad = 1
  if (item.cantidad > item.stock_disponible) item.cantidad = item.stock_disponible
  item.subtotal = item.cantidad * item.precio_unitario
}

const eliminarDelCarrito = (index) => {
  carrito.value.splice(index, 1)
}

const cancelarVenta = () => {
  if (confirm('¿Estás seguro de cancelar esta venta?')) {
    carrito.value = []
    descuento.value = 0
    montoRecibido.value = 0
    notasVenta.value = ''
    ventaOk.value = null
    resultadosBusqueda.value = []
  }
}

// --- PROCESAR VENTA REAL ---
const procesarVenta = async () => {
  if (!puedeCobrar.value) return

  procesando.value = true
  try {
    const payload = {
      items: carrito.value.map(item => ({
        producto_id: item.producto_id,
        cantidad: item.cantidad,
        precio_unitario: item.precio_unitario,
        precio_compra: item.precio_compra,
        subtotal: item.subtotal
      })),
      metodo_pago: metodoPago.value,
      monto_recibido: montoRecibido.value,
      descuento: descuento.value,
      notas: notasVenta.value || null
    }

    const resultado = await posService.procesarVenta(payload)

    ventaOk.value = {
      numero: resultado.numero_venta,
      total: resultado.total,
      cambio: resultado.cambio || 0
    }

    // Actualizar resumen del día
    ventasHoyCount.value++
    totalHoyMonto.value += resultado.total

    // Limpiar carrito
    carrito.value = []
    descuento.value = 0
    montoRecibido.value = 0
    notasVenta.value = ''

  } catch (e) {
    alert('❌ Error al procesar venta: ' + (e.response?.data?.detail || e.message))
  } finally {
    procesando.value = false
  }
}
</script>