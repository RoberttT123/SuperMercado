<template>
  <div class="p-8 pl-10 max-w-full">
    <div class="mb-6 flex justify-between items-end border-b border-[#FFE0CC] pb-4">
      <div>
        <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">🛒 Punto de Venta</h1>
        <p class="text-gray-500 text-sm">Caja #1 · Cajero: {{ cajeroActual }}</p>
      </div>
      <div v-if="!cajaStore.cajaAbierta" class="bg-red-100 text-red-700 px-4 py-2 rounded-lg font-bold border border-red-200">
        🔒 No hay caja abierta. Ve a Control de Caja.
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6" v-if="cajaStore.cajaAbierta">

      <div class="lg:col-span-3 flex flex-col gap-6">

        <div class="bg-white rounded-2xl p-6 shadow-sm border border-[#FFE0CC]">
          <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">📊 Escanear o Buscar Producto</h2>

          <div class="flex gap-4 mb-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="metodoBusqueda" value="codigo" class="text-[#FF6B2B]" />
              <span class="text-sm font-medium">Código de barras</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="metodoBusqueda" value="nombre" class="text-[#FF6B2B]" />
              <span class="text-sm font-medium">Búsqueda por nombre</span>
            </label>
          </div>

          <div v-if="metodoBusqueda === 'codigo'" class="flex gap-3">
            <input type="text" v-model="codigoInput" @keyup.enter="escanearCodigo"
              placeholder="Escanea o escribe el código..."
              class="flex-1 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" autofocus />
            <input type="number" v-model.number="cantidadScan" min="1"
              class="w-24 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" />
          </div>

          <div v-if="metodoBusqueda === 'nombre'">
            <input type="text" v-model="nombreBusq" placeholder="Escribe el nombre... aparece solo"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" autofocus />
          </div>

          <div v-if="errorBusqueda" class="mt-2 p-3 bg-red-50 text-red-600 rounded-lg text-sm border border-red-200">
            {{ errorBusqueda }}
          </div>

          <div v-if="buscando" class="mt-2 text-center text-sm text-gray-500">🔍 Buscando...</div>

          <div v-if="resultadosBusqueda.length > 0"
            class="mt-2 border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            <div v-for="prod in resultadosBusqueda" :key="prod.id"
              class="p-3 border-b border-gray-100 last:border-0 hover:bg-orange-50/50 transition-colors">

              <div class="mb-2">
                <span class="font-bold text-sm">{{ prod.nombre }}</span>
                <span class="text-xs text-gray-400 ml-2">{{ prod.codigo }}</span>
              </div>

              <div v-if="!prod.niveles || prod.niveles.length === 0" class="text-xs text-gray-400 italic">
                ⚠️ Este producto no tiene niveles de venta configurados en Inventario.
              </div>

              <div v-else class="space-y-2">
                <div v-for="nivel in prod.niveles" :key="nivel.id"
                  class="flex items-center justify-between gap-2 bg-gray-50 rounded-lg p-2">
                  <div class="flex items-center gap-2">
                    <span class="text-lg">{{ nivelIcono(nivel.nivel) }}</span>
                    <div class="leading-tight">
                      <div class="font-bold text-sm capitalize">{{ nivel.nivel }} · Bs. {{ nivel.precio_venta.toFixed(2) }}</div>
                      <div class="text-xs" :class="nivel.stock > nivel.stock_minimo ? 'text-green-600' : nivel.stock > 0 ? 'text-yellow-600' : 'text-red-500'">
                        Stock: {{ nivel.stock }}
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <input type="number" min="1" v-model.number="cantidadChip[nivel.id]"
                      class="w-14 px-1 py-1.5 border rounded-lg text-center text-sm focus:outline-none focus:border-[#FF6B2B]">
                    <button @click="agregarAlCarrito(prod, nivel, cantidadChip[nivel.id] || 1)"
                      :disabled="nivel.stock <= 0"
                      class="bg-[#FF6B2B] hover:bg-[#E85510] disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold text-xs py-1.5 px-3 rounded-lg transition-colors">
                      ➕ Agregar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 shadow-sm border border-[#FFE0CC] flex-1">
          <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">🛒 Carrito ({{ carrito.length }} items)</h2>

          <div v-if="carrito.length === 0"
            class="bg-orange-50 text-[#E85510] p-4 rounded-lg text-center border border-orange-100">
            El carrito está vacío. Escanea o busca un producto para comenzar.
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
                  <td class="py-3 font-medium">
                    {{ item.nombre }}
                    <span class="block text-xs text-blue-600 font-normal capitalize">
                      {{ nivelIcono(item.nivelNombre) }} {{ item.nivelNombre }}
                    </span>
                  </td>
                  <td class="py-3">
                    <input type="number" v-model.number="item.cantidad"
                      @input="recalcularSubtotal(item)" min="1"
                      class="w-16 p-1 border rounded text-center focus:outline-none focus:border-[#FF6B2B]" />
                  </td>
                  <td class="py-3">
                    <input type="number" v-model.number="item.precio_unitario"
                      @input="recalcularSubtotal(item)" min="0" step="0.01"
                      class="w-20 p-1 border rounded text-center focus:outline-none focus:border-[#FF6B2B]" />
                    <div v-if="item.precio_unitario < item.precio_compra" class="text-[10px] text-red-500 font-bold mt-0.5">
                      ⚠️ bajo costo (Bs. {{ item.precio_compra.toFixed(2) }})
                    </div>
                  </td>
                  <td class="py-3 font-bold text-[#2A1A0A]">Bs. {{ item.subtotal.toFixed(2) }}</td>
                  <td class="py-3 text-center">
                    <button @click="eliminarDelCarrito(index)"
                      class="text-red-500 hover:text-red-700 bg-red-50 p-2 rounded hover:bg-red-100 transition-colors">
                      🗑️
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2 flex flex-col gap-6">

        <!-- Cliente y crédito -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-[#FFE0CC] flex flex-col gap-3">
          <label class="block text-sm font-bold text-gray-700">👤 Cliente (opcional)</label>

          <div v-if="!clienteSeleccionado">
            <input v-model="busquedaCliente" type="text" placeholder="Buscar cliente por nombre..."
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-sm">
            <div v-if="resultadosClientes.length > 0" class="mt-2 border border-gray-200 rounded-xl overflow-hidden">
              <div v-for="c in resultadosClientes" :key="c.id" @click="seleccionarCliente(c)"
                class="p-2 hover:bg-orange-50 cursor-pointer border-b border-gray-100 last:border-0 text-sm transition-colors">
                <div class="font-bold">{{ c.nombre }}</div>
                <div class="text-xs text-gray-400">Debe: Bs. {{ c.saldo_pendiente.toFixed(2) }} · Límite: Bs. {{ c.limite_credito.toFixed(2) }}</div>
              </div>
            </div>
          </div>
          <div v-else class="flex items-center justify-between bg-orange-50 border border-orange-200 rounded-lg p-3">
            <div>
              <div class="font-bold text-sm">{{ clienteSeleccionado.nombre }}</div>
              <div class="text-xs text-gray-500">Debe: Bs. {{ clienteSeleccionado.saldo_pendiente.toFixed(2) }} · Límite: Bs. {{ clienteSeleccionado.limite_credito.toFixed(2) }}</div>
            </div>
            <button @click="quitarCliente" class="text-red-500 text-xs font-bold hover:underline">✕ Quitar</button>
          </div>

          <label class="flex items-center gap-2 mt-1" :class="{ 'opacity-40 cursor-not-allowed': !puedeVenderCredito }">
            <input type="checkbox" v-model="esCredito" :disabled="!puedeVenderCredito">
            <span class="text-sm font-bold text-gray-700">🧾 Vender a crédito (fiado)</span>
          </label>
          <p v-if="clienteSeleccionado && clienteSeleccionado.limite_credito <= 0" class="text-xs text-red-500 -mt-1">
            ⚠️ Este cliente no tiene línea de crédito habilitada (límite Bs. 0). Edítalo en Clientes si quieres darle crédito.
          </p>

          <div v-if="esCredito" class="bg-gray-50 p-3 rounded-lg border border-gray-200">
            <label class="block text-xs font-bold text-gray-600 mb-1">💵 Monto que paga ahora (Bs.)</label>
            <input type="number" v-model.number="montoRecibido" min="0" step="0.5"
              class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-sm">
            <p class="text-xs mt-2 text-gray-600">
              Queda a crédito: <strong class="text-red-600">Bs. {{ saldoACredito.toFixed(2) }}</strong>
            </p>
            <div v-if="advertenciaCredito" class="mt-2 bg-red-50 text-red-700 text-xs font-bold p-2 rounded-lg border border-red-200">
              ⚠️ {{ advertenciaCredito }}
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 shadow-sm border border-[#FFE0CC] flex flex-col gap-4">

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">🏷️ Descuento (Bs.)</label>
            <input type="number" v-model.number="descuento" min="0" :max="subtotal" step="0.5"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" />
          </div>

          <div class="bg-[#FFF9F6] border-2 border-[#FF6B2B] rounded-xl p-4 text-center mt-2">
            <div class="text-sm font-black text-[#E85510] uppercase tracking-widest mb-1">Total a Pagar</div>
            <div class="text-4xl font-black text-[#2A1A0A]">Bs. {{ total.toFixed(2) }}</div>
          </div>

          <hr class="border-gray-200" />

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">💳 Método de pago:</label>
            <div class="grid grid-cols-3 gap-2">
              <button @click="metodoPago = 'efectivo'"
                :class="['py-2 px-1 text-sm font-bold rounded-lg border transition-colors',
                  metodoPago === 'efectivo' ? 'bg-[#FF6B2B] text-white border-[#FF6B2B]' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50']">
                💵 Efectivo
              </button>
              <button @click="metodoPago = 'qr'"
                :class="['py-2 px-1 text-sm font-bold rounded-lg border transition-colors',
                  metodoPago === 'qr' ? 'bg-[#FF6B2B] text-white border-[#FF6B2B]' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50']">
                📱 QR
              </button>
              <button @click="metodoPago = 'tarjeta'"
                :class="['py-2 px-1 text-sm font-bold rounded-lg border transition-colors',
                  metodoPago === 'tarjeta' ? 'bg-[#FF6B2B] text-white border-[#FF6B2B]' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50']">
                💳 Tarjeta
              </button>
            </div>
          </div>

          <div v-if="metodoPago === 'efectivo' && !esCredito" class="bg-gray-50 p-4 rounded-xl border border-gray-200">
            <label class="block text-sm font-bold text-gray-700 mb-1">💵 Monto recibido (Bs.)</label>
            <input type="number" v-model.number="montoRecibido" min="0"
              class="w-full px-4 py-2 mb-3 rounded-lg border border-gray-300 focus:outline-none focus:border-[#FF6B2B]" />
            <div class="flex justify-between items-center text-lg">
              <span class="font-bold text-gray-600">Cambio:</span>
              <span :class="['font-black text-2xl', cambio >= 0 ? 'text-green-600' : 'text-red-500']">
                Bs. {{ cambio.toFixed(2) }}
              </span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📝 Notas (opcional)</label>
            <input type="text" v-model="notasVenta" placeholder="Detalles de la venta..."
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]" />
          </div>

          <div class="grid grid-cols-2 gap-3 mt-4">
            <button @click="procesarVenta" :disabled="!puedeCobrar"
              :class="['py-3 rounded-xl font-black text-lg transition-all',
                puedeCobrar ? 'bg-[#4CAF50] hover:bg-[#43A047] text-white shadow-md' : 'bg-gray-200 text-gray-400 cursor-not-allowed']">
              {{ procesando ? '⏳...' : '✅ COBRAR' }}
            </button>
            <button @click="cancelarVenta"
              class="py-3 rounded-xl font-bold text-lg border-2 border-gray-200 text-gray-600 hover:bg-gray-50 transition-all">
              🗑️ Cancelar
            </button>
          </div>

          <div v-if="ventaOk" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-xl text-center">
            <div class="text-green-600 text-3xl mb-2">✅</div>
            <h3 class="font-black text-green-800">¡Venta completada!</h3>
            <p class="text-sm text-green-700 mt-1">
              Nº {{ ventaOk.numero }} · Total: <strong>Bs. {{ ventaOk.total.toFixed(2) }}</strong>
            </p>
            <p v-if="ventaOk.cambio > 0" class="text-sm text-green-600 mt-1">
              Cambio: Bs. {{ ventaOk.cambio.toFixed(2) }}
            </p>
            <p class="text-xs text-gray-400 mt-2">📄 Nota de venta generada automáticamente</p>
            <button @click="ventaOk = null"
              class="mt-3 bg-white text-green-700 text-sm font-bold py-1 px-4 rounded border border-green-300 hover:bg-green-100">
              🔄 Nueva venta
            </button>
          </div>
        </div>

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

    <div v-else class="text-center py-16 text-gray-400">
      <div class="text-5xl mb-4">🔒</div>
      <div class="font-bold text-lg">No hay caja abierta</div>
      <p class="text-sm mt-2">Ve a <router-link to="/caja" class="text-[#FF6B2B] font-bold hover:underline">Control de Caja</router-link> para abrir la caja.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useCajaStore } from '@/stores/cajaStore'
import posService from '@/services/posService'
import clientesService from '@/services/clientesService'

const authStore = useAuthStore()
const cajaStore = useCajaStore()

const cajeroActual = ref(authStore.user?.username || 'Cajero')
const ventasHoyCount = ref(0)
const totalHoyMonto = ref(0)

const metodoBusqueda = ref('codigo')
const codigoInput = ref('')
const cantidadScan = ref(1)
const nombreBusq = ref('')
const resultadosBusqueda = ref([])
const buscando = ref(false)
const errorBusqueda = ref('')
const cantidadChip = ref({})

const carrito = ref([])
const descuento = ref(0)
const metodoPago = ref('efectivo')
const montoRecibido = ref(0)
const notasVenta = ref('')
const ventaOk = ref(null)
const procesando = ref(false)

// ── Cliente y crédito ─────────────────────────────────────────────
const busquedaCliente = ref('')
const resultadosClientes = ref([])
const clienteSeleccionado = ref(null)
const esCredito = ref(false)

const puedeVenderCredito = computed(() =>
  !!clienteSeleccionado.value && clienteSeleccionado.value.limite_credito > 0
)

const nivelIcono = (nivel) => ({
  jaba: '🧃', caja: '📦', paquete: '🥡', bolsa: '🛍️', unidad: '🔹'
}[nivel] || '📦')

const subtotal = computed(() =>
  carrito.value.reduce((acc, item) => acc + item.subtotal, 0)
)
const total = computed(() =>
  Math.max(0, subtotal.value - (descuento.value || 0))
)
const cambio = computed(() => {
  if (metodoPago.value !== 'efectivo' || esCredito.value) return 0
  return (montoRecibido.value || 0) - total.value
})
const saldoACredito = computed(() => {
  if (!esCredito.value) return 0
  return Math.max(0, total.value - (montoRecibido.value || 0))
})
const advertenciaCredito = computed(() => {
  if (!esCredito.value || !clienteSeleccionado.value) return null
  const nuevoSaldo = clienteSeleccionado.value.saldo_pendiente + saldoACredito.value
  if (clienteSeleccionado.value.limite_credito > 0 && nuevoSaldo > clienteSeleccionado.value.limite_credito) {
    return `Este cliente quedaría debiendo Bs. ${nuevoSaldo.toFixed(2)}, superando su límite de Bs. ${clienteSeleccionado.value.limite_credito.toFixed(2)}.`
  }
  return null
})
const puedeCobrar = computed(() => {
  if (carrito.value.length === 0) return false
  if (procesando.value) return false
  if (esCredito.value) return puedeVenderCredito.value
  if (metodoPago.value === 'efectivo' && (montoRecibido.value || 0) < total.value) return false
  return true
})

watch(total, (newTotal) => {
  if (metodoPago.value === 'efectivo' && carrito.value.length > 0 && !esCredito.value) {
    montoRecibido.value = newTotal
  }
})

onMounted(async () => {
  await cajaStore.cargarEstado()
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

let debounceClienteTimer = null
watch(busquedaCliente, (val) => {
  clearTimeout(debounceClienteTimer)
  if (!val || val.trim().length < 2) { resultadosClientes.value = []; return }
  debounceClienteTimer = setTimeout(async () => {
    try {
      resultadosClientes.value = await clientesService.buscarCliente(val.trim())
    } catch (e) { console.error(e) }
  }, 300)
})

const seleccionarCliente = (c) => {
  clienteSeleccionado.value = c
  busquedaCliente.value = ''
  resultadosClientes.value = []
  if (c.limite_credito <= 0) esCredito.value = false
}
const quitarCliente = () => {
  clienteSeleccionado.value = null
  esCredito.value = false
}

let debounceTimer = null

const ejecutarBusqueda = async (fn, term) => {
  buscando.value = true
  errorBusqueda.value = ''
  try {
    const resultados = await fn(term)
    resultadosBusqueda.value = resultados
    resultados.forEach(p => (p.niveles || []).forEach(n => {
      if (!(n.id in cantidadChip.value)) cantidadChip.value[n.id] = 1
    }))
    if (resultados.length === 0) {
      errorBusqueda.value = `No se encontró ningún producto con "${term}"`
    }
  } catch (e) {
    errorBusqueda.value = 'Error al buscar producto'
    console.error(e)
  } finally {
    buscando.value = false
  }
}

watch(nombreBusq, (val) => {
  clearTimeout(debounceTimer)
  if (!val || val.trim().length < 2) {
    resultadosBusqueda.value = []
    errorBusqueda.value = ''
    return
  }
  debounceTimer = setTimeout(() => {
    ejecutarBusqueda(posService.buscarPorNombre, val.trim())
  }, 300)
})

const escanearCodigo = async () => {
  const term = codigoInput.value.trim()
  if (!term) return

  buscando.value = true
  errorBusqueda.value = ''
  try {
    const resultados = await posService.buscarPorCodigo(term)
    if (resultados.length === 1 && resultados[0].niveles && resultados[0].niveles.length === 1) {
      agregarAlCarrito(resultados[0], resultados[0].niveles[0], cantidadScan.value)
      codigoInput.value = ''
      cantidadScan.value = 1
      resultadosBusqueda.value = []
    } else if (resultados.length === 0) {
      errorBusqueda.value = `No se encontró ningún producto con código "${term}"`
    } else {
      resultadosBusqueda.value = resultados
      resultados.forEach(p => (p.niveles || []).forEach(n => {
        if (!(n.id in cantidadChip.value)) cantidadChip.value[n.id] = 1
      }))
    }
  } catch (e) {
    errorBusqueda.value = 'Error al buscar producto'
    console.error(e)
  } finally {
    buscando.value = false
  }
}

const agregarAlCarrito = (producto, nivel, cantidad = 1) => {
  if (!nivel || nivel.stock <= 0) {
    alert(`⚠️ No hay stock de "${nivel?.nivel}" para "${producto.nombre}"`)
    return
  }
  if (cantidad <= 0) return
  if (cantidad > nivel.stock) {
    alert(`⚠️ Stock insuficiente. Disponible: ${nivel.stock} ${nivel.nivel}(s)`)
    return
  }

  const index = carrito.value.findIndex(i => i.nivel_id === nivel.id)
  if (index !== -1) {
    const nuevaCantidad = carrito.value[index].cantidad + cantidad
    if (nuevaCantidad > nivel.stock) {
      alert(`⚠️ Stock insuficiente. Disponible: ${nivel.stock}`)
      return
    }
    carrito.value[index].cantidad = nuevaCantidad
    recalcularSubtotal(carrito.value[index])
  } else {
    carrito.value.push({
      producto_id: producto.id,
      nivel_id: nivel.id,
      nivelNombre: nivel.nivel,
      codigo: producto.codigo,
      nombre: producto.nombre,
      precio_unitario: nivel.precio_venta,
      precio_compra: nivel.precio_compra,
      stock_disponible: nivel.stock,
      cantidad: cantidad,
      subtotal: nivel.precio_venta * cantidad
    })
  }

  nombreBusq.value = ''
  resultadosBusqueda.value = []
}

const recalcularSubtotal = (item) => {
  if (item.cantidad < 1) item.cantidad = 1
  if (item.cantidad > item.stock_disponible) item.cantidad = item.stock_disponible
  if (item.precio_unitario < 0 || isNaN(item.precio_unitario)) item.precio_unitario = 0
  item.subtotal = item.cantidad * item.precio_unitario
}

const eliminarDelCarrito = (index) => carrito.value.splice(index, 1)

const cancelarVenta = () => {
  if (confirm('¿Estás seguro de cancelar esta venta?')) {
    carrito.value = []
    descuento.value = 0
    montoRecibido.value = 0
    notasVenta.value = ''
    ventaOk.value = null
    resultadosBusqueda.value = []
    clienteSeleccionado.value = null
    esCredito.value = false
    busquedaCliente.value = ''
  }
}

const procesarVenta = async () => {
  if (!puedeCobrar.value) return
  if (esCredito.value && !puedeVenderCredito.value) {
    alert('⚠️ Este cliente no tiene línea de crédito habilitada')
    return
  }

  procesando.value = true
  try {
    const payload = {
      items: carrito.value.map(item => ({
        producto_id: item.producto_id,
        nivel_id: item.nivel_id,
        cantidad: item.cantidad,
        precio_unitario: item.precio_unitario,
        precio_compra: item.precio_compra,
        subtotal: item.subtotal
      })),
      metodo_pago: metodoPago.value,
      monto_recibido: montoRecibido.value,
      descuento: descuento.value,
      notas: notasVenta.value || null,
      caja_id: cajaStore.cajaId,
      cliente_id: clienteSeleccionado.value?.id || null,
      es_credito: esCredito.value
    }

    const resultado = await posService.procesarVenta(payload)

    ventaOk.value = {
      numero: resultado.numero_venta,
      total: resultado.total,
      cambio: resultado.cambio || 0
    }

    cajaStore.actualizarVentasHoy(resultado.total)
    ventasHoyCount.value++
    totalHoyMonto.value += resultado.total

    // Genera y descarga la nota de venta automáticamente
    try {
      await posService.descargarPDF(resultado.venta_id)
    } catch (e) {
      console.error('No se pudo generar el PDF automáticamente', e)
    }

    carrito.value = []
    descuento.value = 0
    montoRecibido.value = 0
    notasVenta.value = ''
    clienteSeleccionado.value = null
    esCredito.value = false
    busquedaCliente.value = ''

  } catch (e) {
    alert('❌ Error al procesar venta: ' + (e.response?.data?.detail || e.message))
  } finally {
    procesando.value = false
  }
}
</script>