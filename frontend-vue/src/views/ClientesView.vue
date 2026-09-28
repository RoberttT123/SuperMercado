<template>
  <div class="p-8 pl-10 max-w-full">
    <div class="mb-6 border-b border-[#FFE0CC] pb-4">
      <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">👥 Clientes</h1>
      <p class="text-gray-500 text-sm">Gestión de clientes y cuentas por cobrar (fiado).</p>
    </div>

    <div class="mb-6 flex border-b border-gray-200 overflow-x-auto">
      <button @click="activeTab = 'lista'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'lista' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">📋 Lista</button>
      <button @click="activeTab = 'nuevo'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'nuevo' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">➕ Nuevo Cliente</button>
      <button @click="activeTab = 'editar'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'editar' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">✏️ Editar Cliente</button>
      <button @click="activeTab = 'cobranza'; cargarClientes()" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors relative', activeTab === 'cobranza' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        💰 Cuentas por Cobrar
        <span v-if="deudores.length > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-black w-5 h-5 rounded-full flex items-center justify-center">
          {{ deudores.length }}
        </span>
      </button>
    </div>

    <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm mb-10">

      <!-- ══════════════ TAB LISTA ══════════════ -->
      <div v-if="activeTab === 'lista'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Todos los Clientes</h2>
        <input v-model="filtroLista" type="text" placeholder="🔍 Buscar por nombre..."
          class="w-full px-4 py-2 mb-4 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">

        <div v-if="cargando" class="text-center py-8 text-gray-400">⏳ Cargando...</div>
        <div v-else-if="clientesFiltrados.length === 0" class="text-center py-8 text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
          No se encontraron clientes.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                <th class="pb-2">Nombre</th>
                <th class="pb-2">NIT/CI</th>
                <th class="pb-2">Teléfono</th>
                <th class="pb-2 text-right">Límite crédito</th>
                <th class="pb-2 text-right">Saldo pendiente</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="c in clientesFiltrados" :key="c.id" class="hover:bg-orange-50/50">
                <td class="py-3 font-bold">{{ c.nombre }}</td>
                <td class="py-3 text-sm text-gray-500">{{ c.nit_ci || '—' }}</td>
                <td class="py-3 text-sm text-gray-500">{{ c.telefono || '—' }}</td>
                <td class="py-3 text-right text-sm">Bs. {{ c.limite_credito.toFixed(2) }}</td>
                <td class="py-3 text-right font-bold" :class="c.saldo_pendiente > 0 ? 'text-red-600' : 'text-gray-400'">
                  Bs. {{ c.saldo_pendiente.toFixed(2) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ══════════════ TAB NUEVO ══════════════ -->
      <div v-if="activeTab === 'nuevo'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Registrar Nuevo Cliente</h2>
        <form @submit.prevent="guardarNuevoCliente" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">👤 Nombre *</label>
            <input v-model="formNuevo.nombre" type="text" required
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">🪪 NIT / CI</label>
            <input v-model="formNuevo.nit_ci" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📞 Teléfono</label>
            <input v-model="formNuevo.telefono" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">💳 Límite de crédito (Bs.)</label>
            <input v-model.number="formNuevo.limite_credito" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-bold text-gray-700 mb-1">📍 Dirección</label>
            <input v-model="formNuevo.direccion" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="md:col-span-2">
            <button type="submit" :disabled="guardando"
              class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors disabled:opacity-50">
              {{ guardando ? '⏳ Guardando...' : '✅ Guardar Cliente' }}
            </button>
          </div>
        </form>
      </div>

      <!-- ══════════════ TAB EDITAR ══════════════ -->
      <div v-if="activeTab === 'editar'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Editar Cliente</h2>
        <select v-model="clienteAEditarId" @change="cargarDatosEdicion"
          class="w-full px-4 py-2 mb-6 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          <option :value="null">-- Selecciona un cliente --</option>
          <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>

        <form v-if="formEditar" @submit.prevent="actualizarCliente" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">Nombre</label>
            <input v-model="formEditar.nombre" type="text" required
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">NIT / CI</label>
            <input v-model="formEditar.nit_ci" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">Teléfono</label>
            <input v-model="formEditar.telefono" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">Límite de crédito (Bs.)</label>
            <input v-model.number="formEditar.limite_credito" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-bold text-gray-700 mb-1">Dirección</label>
            <input v-model="formEditar.direccion" type="text"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="md:col-span-2 bg-gray-50 rounded-lg p-3 text-sm text-gray-500">
            Saldo pendiente actual: <strong class="text-red-600">Bs. {{ formEditar.saldo_pendiente.toFixed(2) }}</strong>
            (se ajusta solo con ventas a crédito o abonos, no aquí)
          </div>
          <div class="md:col-span-2">
            <button type="submit" :disabled="guardando"
              class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors disabled:opacity-50">
              {{ guardando ? '⏳ Guardando...' : '💾 Actualizar Cliente' }}
            </button>
          </div>
        </form>
        <div v-else class="text-center py-8 text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
          Selecciona un cliente para editarlo.
        </div>
      </div>

      <!-- ══════════════ TAB COBRANZA ══════════════ -->
      <div v-if="activeTab === 'cobranza'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-1">💰 Cuentas por Cobrar</h2>
        <p class="text-sm text-gray-500 mb-6">Clientes con saldo pendiente. Haz clic para ver el detalle y registrar un abono.</p>

        <div v-if="deudores.length === 0" class="bg-green-50 text-green-700 p-4 rounded-lg font-bold text-center border border-green-200">
          ✅ Ningún cliente tiene saldo pendiente.
        </div>

        <div v-else class="space-y-3">
          <div v-for="c in deudores" :key="c.id" class="border border-gray-200 rounded-xl overflow-hidden">
            <div class="flex items-center justify-between p-4 bg-gray-50 cursor-pointer" @click="toggleDeudor(c)">
              <div>
                <div class="font-bold text-gray-800">{{ c.nombre }}</div>
                <div class="text-xs text-gray-400">{{ c.telefono || 'sin teléfono' }}</div>
              </div>
              <div class="flex items-center gap-3">
                <span class="font-black text-red-600">Bs. {{ c.saldo_pendiente.toFixed(2) }}</span>
                <span class="text-gray-400">{{ deudorAbierto === c.id ? '▲' : '▼' }}</span>
              </div>
            </div>

            <div v-if="deudorAbierto === c.id" class="p-4 border-t border-gray-100">
              <div v-if="!movimientosPorCliente[c.id]" class="text-center py-4 text-gray-400">⏳ Cargando...</div>
              <div v-else>
                <div class="text-xs font-bold text-gray-500 uppercase mb-2">Historial</div>
                <div class="space-y-1 mb-4 max-h-48 overflow-y-auto">
                  <div v-for="m in movimientosPorCliente[c.id]" :key="m.id"
                    class="flex justify-between text-sm py-1.5 border-b border-gray-100 last:border-0">
                    <span :class="m.tipo === 'cargo' ? 'text-red-600' : 'text-green-600'" class="font-bold">
                      {{ m.tipo === 'cargo' ? '🔴 Cargo' : '🟢 Abono' }}
                      <span v-if="m.ventas" class="text-gray-400 font-normal">· {{ m.ventas.numero_venta }}</span>
                    </span>
                    <span class="font-bold">Bs. {{ m.monto.toFixed(2) }}</span>
                  </div>
                </div>

                <div class="bg-gray-50 p-3 rounded-xl border border-gray-200 flex gap-3 items-end">
                  <div class="flex-1">
                    <label class="block text-xs font-bold text-gray-600 mb-1">💵 Registrar abono (Bs.)</label>
                    <input type="number" min="0.01" step="0.01" v-model.number="montoAbono[c.id]"
                      class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-sm">
                  </div>
                  <button @click="registrarAbono(c)" :disabled="!montoAbono[c.id]"
                    class="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold px-4 py-2 rounded-lg text-sm">
                    ✅ Registrar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import clientesService from '@/services/clientesService'

const activeTab = ref('lista')
const cargando = ref(false)
const guardando = ref(false)

const clientes = ref([])
const filtroLista = ref('')

const clientesFiltrados = computed(() =>
  clientes.value.filter(c => c.nombre.toLowerCase().includes(filtroLista.value.toLowerCase()))
)

const cargarClientes = async () => {
  cargando.value = true
  try {
    clientes.value = await clientesService.getClientes()
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

onMounted(cargarClientes)

// ── NUEVO ──────────────────────────────────────────
const formNuevo = ref({ nombre: '', nit_ci: '', telefono: '', direccion: '', limite_credito: 0 })

const guardarNuevoCliente = async () => {
  guardando.value = true
  try {
    await clientesService.crearCliente(formNuevo.value)
    alert(`✅ Cliente "${formNuevo.value.nombre}" registrado`)
    formNuevo.value = { nombre: '', nit_ci: '', telefono: '', direccion: '', limite_credito: 0 }
    await cargarClientes()
    activeTab.value = 'lista'
  } catch (e) {
    alert('❌ Error al guardar: ' + (e.response?.data?.detail || e.message))
  } finally {
    guardando.value = false
  }
}

// ── EDITAR ─────────────────────────────────────────
const clienteAEditarId = ref(null)
const formEditar = ref(null)

const cargarDatosEdicion = () => {
  if (!clienteAEditarId.value) { formEditar.value = null; return }
  const c = clientes.value.find(x => x.id === clienteAEditarId.value)
  if (c) formEditar.value = { ...c }
}

const actualizarCliente = async () => {
  guardando.value = true
  try {
    await clientesService.actualizarCliente(formEditar.value.id, {
      nombre: formEditar.value.nombre,
      nit_ci: formEditar.value.nit_ci,
      telefono: formEditar.value.telefono,
      direccion: formEditar.value.direccion,
      limite_credito: formEditar.value.limite_credito
    })
    alert(`✅ "${formEditar.value.nombre}" actualizado`)
    await cargarClientes()
  } catch (e) {
    alert('❌ Error al actualizar: ' + (e.response?.data?.detail || e.message))
  } finally {
    guardando.value = false
  }
}

// ── COBRANZA ───────────────────────────────────────
const deudores = computed(() => clientes.value.filter(c => c.saldo_pendiente > 0))
const deudorAbierto = ref(null)
const movimientosPorCliente = ref({})
const montoAbono = ref({})

const toggleDeudor = async (c) => {
  if (deudorAbierto.value === c.id) { deudorAbierto.value = null; return }
  deudorAbierto.value = c.id
  if (!movimientosPorCliente.value[c.id]) {
    try {
      movimientosPorCliente.value[c.id] = await clientesService.getMovimientos(c.id)
    } catch (e) { console.error(e) }
  }
}

const registrarAbono = async (c) => {
  const monto = montoAbono.value[c.id]
  if (!monto || monto <= 0) return
  try {
    await clientesService.registrarAbono(c.id, monto, 'Abono a cuenta')
    montoAbono.value[c.id] = null
    delete movimientosPorCliente.value[c.id]
    await cargarClientes()
    await toggleDeudor(c)
    await toggleDeudor(c)
  } catch (e) {
    alert('❌ Error al registrar abono: ' + (e.response?.data?.detail || e.message))
  }
}
</script>