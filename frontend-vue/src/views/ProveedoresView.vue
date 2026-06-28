<template>
  <div class="p-8 pl-10 max-w-full">
    <div class="mb-6 border-b border-[#FFE0CC] pb-4">
      <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">🏭 Proveedores</h1>
      <p class="text-gray-500 text-sm">Gestión de proveedores e historial de compras.</p>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 mb-6">
      <button @click="activeTab = 'lista'"
        :class="['px-6 py-3 font-bold text-sm transition-colors', activeTab === 'lista' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        📋 Lista
      </button>
      <button @click="activeTab = 'nuevo'"
        :class="['px-6 py-3 font-bold text-sm transition-colors', activeTab === 'nuevo' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        ➕ Nuevo Proveedor
      </button>
      <button v-if="proveedorSeleccionado" @click="activeTab = 'editar'"
        :class="['px-6 py-3 font-bold text-sm transition-colors', activeTab === 'editar' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        ✏️ Editar
      </button>
      <button v-if="proveedorSeleccionado" @click="activeTab = 'compras'"
        :class="['px-6 py-3 font-bold text-sm transition-colors', activeTab === 'compras' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        📦 Historial de Compras
      </button>
    </div>

    <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm">

      <!-- LISTA -->
      <div v-if="activeTab === 'lista'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold text-[#FF6B2B]">Todos los Proveedores</h2>
          <input v-model="busqueda" type="text" placeholder="🔍 Buscar..."
            class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-sm w-64">
        </div>

        <div v-if="cargando" class="text-center py-8 text-gray-400">⏳ Cargando...</div>

        <div v-else-if="proveedoresFiltrados.length === 0"
          class="text-center py-8 text-gray-400 bg-gray-50 rounded-xl border border-gray-200">
          No se encontraron proveedores.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                <th class="pb-2">Nombre</th>
                <th class="pb-2">Contacto</th>
                <th class="pb-2">Teléfono</th>
                <th class="pb-2">Dirección</th>
                <th class="pb-2 text-center">Estado</th>
                <th class="pb-2 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="p in proveedoresFiltrados" :key="p.id" class="hover:bg-orange-50/50">
                <td class="py-3 font-bold text-gray-800">{{ p.nombre }}</td>
                <td class="py-3 text-sm text-gray-600">{{ p.contacto || '—' }}</td>
                <td class="py-3 text-sm text-gray-600">{{ p.telefono || '—' }}</td>
                <td class="py-3 text-sm text-gray-600">{{ p.direccion || '—' }}</td>
                <td class="py-3 text-center">
                  <span v-if="p.activo"
                    class="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full">✅ Activo</span>
                  <span v-else
                    class="bg-red-100 text-red-500 text-xs font-bold px-2 py-1 rounded-full">❌ Inactivo</span>
                </td>
                <td class="py-3 text-center">
                  <div class="flex justify-center gap-2">
                    <button @click="seleccionarProveedor(p); activeTab = 'editar'"
                      class="text-xs bg-blue-50 text-blue-600 font-bold px-3 py-1 rounded-lg hover:bg-blue-100 transition-colors">
                      ✏️ Editar
                    </button>
                    <button @click="seleccionarProveedor(p); activeTab = 'compras'"
                      class="text-xs bg-orange-50 text-[#FF6B2B] font-bold px-3 py-1 rounded-lg hover:bg-orange-100 transition-colors">
                      📦 Compras
                    </button>
                    <button v-if="p.activo" @click="toggleActivo(p)"
                      class="text-xs bg-red-50 text-red-500 font-bold px-3 py-1 rounded-lg hover:bg-red-100 transition-colors">
                      🚫 Desactivar
                    </button>
                    <button v-else @click="toggleActivo(p)"
                      class="text-xs bg-green-50 text-green-600 font-bold px-3 py-1 rounded-lg hover:bg-green-100 transition-colors">
                      ✅ Activar
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <p class="text-xs text-gray-400 mt-3">{{ proveedoresFiltrados.length }} proveedor(es)</p>
        </div>
      </div>

      <!-- NUEVO -->
      <div v-if="activeTab === 'nuevo'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-6">Registrar Nuevo Proveedor</h2>
        <form @submit.prevent="guardarNuevo" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">🏭 Nombre *</label>
            <input v-model="formNuevo.nombre" type="text" required placeholder="Ej: Distribuidora Norte"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">👤 Contacto</label>
            <input v-model="formNuevo.contacto" type="text" placeholder="Nombre del representante"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📞 Teléfono</label>
            <input v-model="formNuevo.telefono" type="text" placeholder="Ej: 7712 3456"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📍 Dirección</label>
            <input v-model="formNuevo.direccion" type="text" placeholder="Ej: Av. Principal #123"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="md:col-span-2">
            <button type="submit" :disabled="guardando"
              class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors disabled:opacity-50">
              {{ guardando ? '⏳ Guardando...' : '✅ Registrar Proveedor' }}
            </button>
          </div>
        </form>
      </div>

      <!-- EDITAR -->
      <div v-if="activeTab === 'editar' && proveedorSeleccionado">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-6">Editar: {{ proveedorSeleccionado.nombre }}</h2>
        <form @submit.prevent="guardarEdicion" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">🏭 Nombre *</label>
            <input v-model="formEditar.nombre" type="text" required
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">👤 Contacto</label>
            <input v-model="formEditar.contacto" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📞 Teléfono</label>
            <input v-model="formEditar.telefono" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📍 Dirección</label>
            <input v-model="formEditar.direccion" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="md:col-span-2 flex gap-4">
            <button type="submit" :disabled="guardando"
              class="flex-1 bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors disabled:opacity-50">
              {{ guardando ? '⏳ Guardando...' : '💾 Guardar Cambios' }}
            </button>
            <button type="button" @click="activeTab = 'lista'"
              class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-lg transition-colors">
              Cancelar
            </button>
          </div>
        </form>
      </div>

      <!-- HISTORIAL COMPRAS -->
      <div v-if="activeTab === 'compras' && proveedorSeleccionado">
        <div class="flex items-center gap-4 mb-6">
          <div>
            <h2 class="text-lg font-bold text-[#FF6B2B]">📦 Compras — {{ proveedorSeleccionado.nombre }}</h2>
            <p class="text-xs text-gray-400 mt-1">Últimas 20 compras registradas</p>
          </div>
        </div>

        <div v-if="cargandoCompras" class="text-center py-8 text-gray-400">⏳ Cargando...</div>

        <div v-else-if="comprasProveedor.length === 0"
          class="text-center py-8 text-gray-400 bg-gray-50 rounded-xl border border-gray-200">
          No hay compras registradas para este proveedor.
        </div>

        <div v-else>
          <!-- Resumen rápido -->
          <div class="grid grid-cols-3 gap-4 mb-6">
            <div class="bg-[#FFF9F6] rounded-xl p-4 border border-[#FFE0CC] text-center">
              <div class="text-xs text-gray-400 uppercase font-bold mb-1">Total Compras</div>
              <div class="text-2xl font-black text-[#FF6B2B]">{{ comprasProveedor.length }}</div>
            </div>
            <div class="bg-[#FFF9F6] rounded-xl p-4 border border-[#FFE0CC] text-center">
              <div class="text-xs text-gray-400 uppercase font-bold mb-1">Monto Total</div>
              <div class="text-2xl font-black text-[#FF6B2B]">
                Bs. {{ totalComprasProveedor.toFixed(2) }}
              </div>
            </div>
            <div class="bg-[#FFF9F6] rounded-xl p-4 border border-[#FFE0CC] text-center">
              <div class="text-xs text-gray-400 uppercase font-bold mb-1">Última Compra</div>
              <div class="text-sm font-black text-[#FF6B2B]">
                {{ formatoFecha(comprasProveedor[0]?.fecha) }}
              </div>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                  <th class="pb-2">Nº Compra</th>
                  <th class="pb-2">Fecha</th>
                  <th class="pb-2 text-right">Total</th>
                  <th class="pb-2 text-center">Estado</th>
                  <th class="pb-2">Notas</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="c in comprasProveedor" :key="c.id" class="hover:bg-gray-50">
                  <td class="py-3 font-bold text-[#FF6B2B]">{{ c.numero_compra }}</td>
                  <td class="py-3 text-sm">{{ formatoFecha(c.fecha) }}</td>
                  <td class="py-3 text-right font-bold">Bs. {{ c.total.toFixed(2) }}</td>
                  <td class="py-3 text-center">
                    <span class="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full">
                      {{ c.estado }}
                    </span>
                  </td>
                  <td class="py-3 text-sm text-gray-400">{{ c.notas || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import proveedoresService from '@/services/proveedoresService'

const activeTab = ref('lista')
const cargando = ref(false)
const guardando = ref(false)
const cargandoCompras = ref(false)
const busqueda = ref('')

const proveedores = ref([])
const proveedorSeleccionado = ref(null)
const comprasProveedor = ref([])

const formNuevo = ref({ nombre: '', contacto: '', telefono: '', direccion: '' })
const formEditar = ref({ nombre: '', contacto: '', telefono: '', direccion: '' })

// --- COMPUTADOS ---
const proveedoresFiltrados = computed(() =>
  proveedores.value.filter(p =>
    p.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) ||
    (p.contacto || '').toLowerCase().includes(busqueda.value.toLowerCase()) ||
    (p.telefono || '').includes(busqueda.value)
  )
)

const totalComprasProveedor = computed(() =>
  comprasProveedor.value.reduce((acc, c) => acc + c.total, 0)
)

// --- CARGAR ---
onMounted(async () => {
  await cargarProveedores()
})

const cargarProveedores = async () => {
  cargando.value = true
  try {
    proveedores.value = await proveedoresService.getProveedores()
  } catch (e) {
    alert('❌ Error al cargar proveedores')
  } finally {
    cargando.value = false
  }
}

// Cuando cambia a tab compras, cargar historial
watch(activeTab, async (tab) => {
  if (tab === 'compras' && proveedorSeleccionado.value) {
    cargandoCompras.value = true
    try {
      comprasProveedor.value = await proveedoresService.getComprasProveedor(proveedorSeleccionado.value.id)
    } catch (e) {
      console.error(e)
    } finally {
      cargandoCompras.value = false
    }
  }
})

// --- ACCIONES ---
const seleccionarProveedor = (p) => {
  proveedorSeleccionado.value = p
  formEditar.value = {
    nombre: p.nombre,
    contacto: p.contacto || '',
    telefono: p.telefono || '',
    direccion: p.direccion || ''
  }
}

const guardarNuevo = async () => {
  guardando.value = true
  try {
    await proveedoresService.crearProveedor(formNuevo.value)
    alert(`✅ Proveedor "${formNuevo.value.nombre}" creado`)
    formNuevo.value = { nombre: '', contacto: '', telefono: '', direccion: '' }
    await cargarProveedores()
    activeTab.value = 'lista'
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error al crear proveedor'))
  } finally {
    guardando.value = false
  }
}

const guardarEdicion = async () => {
  guardando.value = true
  try {
    await proveedoresService.actualizarProveedor(proveedorSeleccionado.value.id, formEditar.value)
    alert(`✅ Proveedor actualizado`)
    await cargarProveedores()
    activeTab.value = 'lista'
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error al actualizar'))
  } finally {
    guardando.value = false
  }
}

const toggleActivo = async (p) => {
  const accion = p.activo ? 'desactivar' : 'activar'
  if (!confirm(`¿Confirmas ${accion} a "${p.nombre}"?`)) return
  try {
    if (p.activo) {
      await proveedoresService.desactivarProveedor(p.id)
    } else {
      await proveedoresService.actualizarProveedor(p.id, { activo: true })
    }
    await cargarProveedores()
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error'))
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