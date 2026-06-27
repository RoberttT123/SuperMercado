<template>
  <div class="p-8 pl-10 max-w-full"><!-- Loading y error -->
<div v-if="loading" class="text-center py-4 text-[#FF6B2B] font-bold">⏳ Cargando...</div>
<div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg">{{ error }}</div>
    <div class="mb-6 border-b border-[#FFE0CC] pb-4">
      <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">📦 Inventario</h1>
      <p class="text-gray-500 text-sm">Gestión de productos, stock y registro de compras.</p>
    </div>

    <div v-if="stockCritico.length > 0" class="mb-6">
      <details class="group bg-[#FFF9F6] border border-[#FF6B2B] rounded-xl shadow-sm open:bg-white transition-all">
        <summary class="cursor-pointer p-4 font-bold text-[#E85510] flex items-center justify-between">
          <span>⚠️ {{ stockCritico.length }} producto(s) con stock crítico — clic para ver</span>
          <span class="transition group-open:rotate-180">▼</span>
        </summary>
        <div class="p-4 pt-0 space-y-2 border-t border-orange-100 mt-2">
          <div v-for="p in stockCritico" :key="p.id" class="bg-[#3a1e1e] border-l-4 border-red-500 text-white p-2 px-4 rounded text-sm flex justify-between">
            <span>🔴 <strong>{{ p.nombre }}</strong></span>
            <span>Stock: {{ p.stock }} / Mínimo: {{ p.stock_minimo }}</span>
          </div>
        </div>
      </details>
    </div>

    <div class="mb-6 flex border-b border-gray-200 overflow-x-auto">
      <button @click="activeTab = 'lista'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'lista' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        📋 Lista de Productos
      </button>
      <button @click="activeTab = 'nuevo'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'nuevo' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        ➕ Nuevo Producto
      </button>
      <button @click="activeTab = 'editar'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'editar' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        ✏️ Editar Producto
      </button>
      <button @click="activeTab = 'compra'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'compra' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        📥 Registrar Compra
      </button>
    </div>

    <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm mb-10">

      <div v-if="activeTab === 'lista'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Todos los Productos</h2>
        
        <div class="flex flex-col md:flex-row gap-4 mb-6">
          <div class="flex-1">
            <input type="text" v-model="filtros.busqueda" placeholder="🔍 Buscar por nombre o código..." class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="w-full md:w-64">
            <select v-model="filtros.categoria" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              <option value="">— Todas las categorías —</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.nombre">{{ cat.nombre }}</option>
            </select>
          </div>
        </div>

        <div v-if="productosFiltrados.length === 0" class="text-center py-8 text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
          No se encontraron productos.
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                <th class="pb-2">Código</th>
                <th class="pb-2">Nombre</th>
                <th class="pb-2">Categoría</th>
                <th class="pb-2 text-right">Compra</th>
                <th class="pb-2 text-right">Venta</th>
                <th class="pb-2 text-right">Margen</th>
                <th class="pb-2 text-center">Stock</th>
                <th class="pb-2 text-center">Mín.</th>
                <th class="pb-2 text-center">Estado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="p in productosFiltrados" :key="p.id" class="hover:bg-orange-50/50">
                <td class="py-3 text-sm text-gray-500">{{ p.codigo }}</td>
                <td class="py-3 font-medium">{{ p.nombre }}</td>
                <td class="py-3 text-sm">{{ p.categoria || '—' }}</td>
                <td class="py-3 text-right text-sm">Bs. {{ p.precio_compra.toFixed(2) }}</td>
                <td class="py-3 text-right font-bold">Bs. {{ p.precio_venta.toFixed(2) }}</td>
                <td class="py-3 text-right text-sm text-gray-500">{{ calcularMargen(p.precio_compra, p.precio_venta) }}%</td>
                <td class="py-3 text-center font-bold" :class="p.stock <= p.stock_minimo ? 'text-red-600' : ''">{{ p.stock }}</td>
                <td class="py-3 text-center text-sm text-gray-400">{{ p.stock_minimo }}</td>
                <td class="py-3 text-center text-sm">
                  <span v-if="p.stock > p.stock_minimo">✅</span>
                  <span v-else title="Stock Crítico">⚠️</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p class="text-xs text-gray-400 mt-3">Total: {{ productosFiltrados.length }} productos</p>
        </div>
      </div>

      <div v-if="activeTab === 'nuevo'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Registrar Nuevo Producto</h2>
        
        <form @submit.prevent="guardarNuevoProducto" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📊 Código de barras *</label>
                <input v-model="formNuevo.codigo" type="text" required placeholder="Ej: 7500123456789" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📝 Nombre del producto *</label>
                <input v-model="formNuevo.nombre" type="text" required placeholder="Ej: Arroz Superior 1kg" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">🏷️ Categoría</label>
                <select v-model="formNuevo.categoria" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  <option value="">— Sin categoría —</option>
                  <option v-for="cat in categorias" :key="cat.id" :value="cat.nombre">{{ cat.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📐 Unidad de medida</label>
                <select v-model="formNuevo.unidad" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  <option value="unidad">unidad</option>
                  <option value="kg">kg</option>
                  <option value="litro">litro</option>
                  <option value="caja">caja</option>
                  <option value="bolsa">bolsa</option>
                  <option value="paquete">paquete</option>
                </select>
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">💸 Precio de compra (Bs.)</label>
                <input v-model.number="formNuevo.precio_compra" type="number" step="0.1" min="0" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">💰 Precio de venta (Bs.) *</label>
                <input v-model.number="formNuevo.precio_venta" type="number" step="0.1" min="0" required class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-bold text-gray-700 mb-1">📦 Stock inicial</label>
                  <input v-model.number="formNuevo.stock" type="number" step="1" min="0" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                </div>
                <div>
                  <label class="block text-sm font-bold text-gray-700 mb-1">⚠️ Stock mínimo</label>
                  <input v-model.number="formNuevo.stock_minimo" type="number" step="1" min="0" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📄 Descripción (opcional)</label>
            <textarea v-model="formNuevo.descripcion" rows="2" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]"></textarea>
          </div>

          <div v-if="formNuevo.precio_compra > 0 && formNuevo.precio_venta > 0" class="bg-blue-50 text-blue-700 p-4 rounded-lg text-sm border border-blue-200">
            💡 Margen de ganancia: <strong>{{ calcularMargen(formNuevo.precio_compra, formNuevo.precio_venta) }}%</strong> — Ganancia por unidad: <strong>Bs. {{ (formNuevo.precio_venta - formNuevo.precio_compra).toFixed(2) }}</strong>
          </div>

          <button type="submit" class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors text-lg">
            ✅ Guardar Producto
          </button>
        </form>
      </div>

      <div v-if="activeTab === 'editar'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Editar Producto Existente</h2>
        
        <div class="mb-6">
          <label class="block text-sm font-bold text-gray-700 mb-1">🔍 Buscar o seleccionar producto a editar</label>
          <select v-model="productoAEditarId" @change="cargarDatosEdicion" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            <option :value="null">-- Seleccione un producto --</option>
            <option v-for="p in productos" :key="p.id" :value="p.id">{{ p.codigo }} — {{ p.nombre }}</option>
          </select>
        </div>

        <div v-if="formEditar" class="border-t border-gray-100 pt-6">
          <form @submit.prevent="actualizarProducto" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Nombre</label>
                <input v-model="formEditar.nombre" type="text" required class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Categoría</label>
                <select v-model="formEditar.categoria" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  <option value="">— Sin categoría —</option>
                  <option v-for="cat in categorias" :key="cat.id" :value="cat.nombre">{{ cat.nombre }}</option>
                </select>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-bold text-gray-700 mb-1">Precio compra (Bs.)</label>
                  <input v-model.number="formEditar.precio_compra" type="number" step="0.1" min="0" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                </div>
                <div>
                  <label class="block text-sm font-bold text-gray-700 mb-1">Precio venta (Bs.)</label>
                  <input v-model.number="formEditar.precio_venta" type="number" step="0.1" min="0" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-bold text-gray-700 mb-1">Stock actual</label>
                  <input v-model.number="formEditar.stock" type="number" step="1" min="0" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                </div>
                <div>
                  <label class="block text-sm font-bold text-gray-700 mb-1">Stock mínimo</label>
                  <input v-model.number="formEditar.stock_minimo" type="number" step="1" min="0" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                </div>
              </div>
            </div>
            
            <div class="md:col-span-2">
              <button type="submit" class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors">
                💾 Actualizar Producto
              </button>
            </div>
          </form>
        </div>
        <div v-else class="text-center py-8 text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
          Selecciona un producto de la lista para editar sus detalles.
        </div>
      </div>

      <div v-if="activeTab === 'compra'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-1">📥 Registrar Compra / Ingreso de Mercadería</h2>
        <p class="text-sm text-gray-500 mb-6">Agrega productos al carrito de compra para actualizar el stock.</p>

        <div class="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-6 flex flex-wrap items-end gap-4">
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-bold text-gray-700 mb-1">📊 Producto</label>
            <select v-model="compraTemp.productoId" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              <option :value="null">-- Seleccionar producto --</option>
              <option v-for="p in productos" :key="p.id" :value="p.id">{{ p.codigo }} — {{ p.nombre }}</option>
            </select>
          </div>
          <div class="w-24">
            <label class="block text-sm font-bold text-gray-700 mb-1">Cantidad</label>
            <input v-model.number="compraTemp.cantidad" type="number" min="1" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="w-32">
            <label class="block text-sm font-bold text-gray-700 mb-1">P. Unit. (Bs.)</label>
            <input v-model.number="compraTemp.precio" type="number" step="0.5" min="0" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <button @click="agregarAlCarrito" :disabled="!compraTemp.productoId" class="bg-gray-800 hover:bg-black text-white font-bold py-2 px-6 rounded-lg transition-colors disabled:opacity-50">
            ➕ Agregar
          </button>
        </div>

        <div v-if="carritoCompra.length > 0">
          <h3 class="font-bold text-gray-700 mb-3">Carrito de Compra</h3>
          <div class="border border-gray-200 rounded-xl overflow-hidden mb-4">
            <div v-for="(item, index) in carritoCompra" :key="index" class="flex items-center justify-between p-3 border-b border-gray-100 last:border-0 hover:bg-gray-50">
              <div class="flex-1 font-medium">{{ item.nombre }}</div>
              <div class="w-24 text-center text-gray-600">x{{ item.cantidad }}</div>
              <div class="w-32 text-right font-bold">Bs. {{ item.subtotal.toFixed(2) }}</div>
              <div class="w-16 text-right">
                <button @click="eliminarDelCarrito(index)" class="text-red-500 hover:text-red-700 font-bold px-2">🗑️</button>
              </div>
            </div>
          </div>
          
          <div class="text-right text-xl font-black text-[#2A1A0A] mb-6">
            Total compra: Bs. {{ totalCarrito.toFixed(2) }}
          </div>
          
          <div class="mb-6">
            <label class="block text-sm font-bold text-gray-700 mb-1">Notas (factura, proveedor, etc.)</label>
            <input v-model="notasCompra" type="text" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>

          <div class="flex gap-4">
            <button @click="registrarCompra" class="flex-1 bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors">
              ✅ Registrar Compra
            </button>
            <button @click="carritoCompra = []" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-lg transition-colors">
              🗑️ Limpiar carrito
            </button>
          </div>
        </div>
        
        <div v-else class="text-center py-8 text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
          El carrito está vacío. Agrega productos arriba para registrar una compra.
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import inventarioService from '@/services/inventarioService'

const activeTab = ref('lista')
const loading = ref(false)
const error = ref(null)

// --- DATOS REALES ---
const categorias = ref([])
const productos = ref([])

// --- CARGAR AL MONTAR ---
onMounted(async () => {
  await cargarDatos()
})

const cargarDatos = async () => {
  loading.value = true
  error.value = null
  try {
    const [prods, cats] = await Promise.all([
      inventarioService.getProductos(),
      inventarioService.getCategorias()
    ])
    productos.value = prods
    categorias.value = cats
  } catch (e) {
    error.value = 'Error al cargar datos. Verifica tu conexión.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

// --- FILTROS ---
const filtros = ref({ busqueda: '', categoria: '' })

const productosFiltrados = computed(() => {
  return productos.value.filter(p => {
    const coincideBusqueda =
      p.nombre.toLowerCase().includes(filtros.value.busqueda.toLowerCase()) ||
      p.codigo.includes(filtros.value.busqueda)
    const coincideCategoria =
      filtros.value.categoria === '' || p.categoria === filtros.value.categoria
    return coincideBusqueda && coincideCategoria
  })
})

const stockCritico = computed(() =>
  productos.value.filter(p => p.stock <= p.stock_minimo)
)

const calcularMargen = (compra, venta) => {
  if (!compra || compra === 0) return 100.0
  return (((venta - compra) / compra) * 100).toFixed(1)
}

// --- NUEVO PRODUCTO ---
const formNuevo = ref({
  codigo: '', nombre: '', categoria_id: null, unidad: 'unidad',
  precio_compra: 0, precio_venta: 0, stock: 0, stock_minimo: 5, descripcion: ''
})

const guardarNuevoProducto = async () => {
  loading.value = true
  try {
    await inventarioService.crearProducto(formNuevo.value)
    alert(`✅ Producto "${formNuevo.value.nombre}" guardado con éxito`)
    formNuevo.value = {
      codigo: '', nombre: '', categoria_id: null, unidad: 'unidad',
      precio_compra: 0, precio_venta: 0, stock: 0, stock_minimo: 5, descripcion: ''
    }
    await cargarDatos()
    activeTab.value = 'lista'
  } catch (e) {
    alert('❌ Error al guardar: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

// --- EDITAR PRODUCTO ---
const productoAEditarId = ref(null)
const formEditar = ref(null)

const cargarDatosEdicion = () => {
  if (!productoAEditarId.value) { formEditar.value = null; return }
  const prod = productos.value.find(p => p.id === productoAEditarId.value)
  if (prod) formEditar.value = { ...prod }
}

const actualizarProducto = async () => {
  loading.value = true
  try {
    await inventarioService.actualizarProducto(formEditar.value.id, {
      nombre: formEditar.value.nombre,
      categoria_id: formEditar.value.categoria_id,
      precio_compra: formEditar.value.precio_compra,
      precio_venta: formEditar.value.precio_venta,
      stock: formEditar.value.stock,
      stock_minimo: formEditar.value.stock_minimo
    })
    alert(`✅ Producto "${formEditar.value.nombre}" actualizado`)
    productoAEditarId.value = null
    formEditar.value = null
    await cargarDatos()
  } catch (e) {
    alert('❌ Error al actualizar: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

// --- COMPRAS ---
const compraTemp = ref({ productoId: null, cantidad: 1, precio: 0 })
const carritoCompra = ref([])
const notasCompra = ref('')

watch(() => compraTemp.value.productoId, (newId) => {
  if (newId) {
    const prod = productos.value.find(p => p.id === newId)
    if (prod) compraTemp.value.precio = prod.precio_compra
  } else {
    compraTemp.value.precio = 0
  }
})

const agregarAlCarrito = () => {
  if (!compraTemp.value.productoId) return
  const prod = productos.value.find(p => p.id === compraTemp.value.productoId)
  carritoCompra.value.push({
    productoId: prod.id,
    nombre: prod.nombre,
    cantidad: compraTemp.value.cantidad,
    precio_unitario: compraTemp.value.precio,
    subtotal: compraTemp.value.cantidad * compraTemp.value.precio
  })
  compraTemp.value = { productoId: null, cantidad: 1, precio: 0 }
}

const eliminarDelCarrito = (index) => carritoCompra.value.splice(index, 1)

const totalCarrito = computed(() =>
  carritoCompra.value.reduce((acc, item) => acc + item.subtotal, 0)
)

const registrarCompra = async () => {
  loading.value = true
  try {
    const result = await inventarioService.registrarCompra(carritoCompra.value, notasCompra.value)
    alert(`✅ Compra ${result.numero_compra} registrada por Bs. ${result.total.toFixed(2)}`)
    carritoCompra.value = []
    notasCompra.value = ''
    await cargarDatos()
  } catch (e) {
    alert('❌ Error al registrar compra: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
</script>