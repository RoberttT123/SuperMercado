<template>
  <div class="p-8 pl-10 max-w-full">
    <div v-if="loading" class="text-center py-4 text-[#FF6B2B] font-bold">⏳ Cargando...</div>
    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg">{{ error }}</div>

    <div class="mb-6 border-b border-[#FFE0CC] pb-4">
      <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">📦 Inventario</h1>
      <p class="text-gray-500 text-sm">Cada producto se vende en un nivel (Jaba, Caja, etc.) que puede indicar cuántas subclases contiene, solo como referencia.</p>
    </div>

    <div v-if="stockCritico.length > 0" class="mb-6">
      <details class="group bg-[#FFF9F6] border border-[#FF6B2B] rounded-xl shadow-sm open:bg-white transition-all">
        <summary class="cursor-pointer p-4 font-bold text-[#E85510] flex items-center justify-between">
          <span>⚠️ {{ stockCritico.length }} nivel(es) con stock crítico — clic para ver</span>
          <span class="transition group-open:rotate-180">▼</span>
        </summary>
        <div class="p-4 pt-0 space-y-2 border-t border-orange-100 mt-2">
          <div v-for="(item, i) in stockCritico" :key="i"
            class="bg-[#3a1e1e] border-l-4 border-red-500 text-white p-2 px-4 rounded text-sm flex justify-between">
            <span>🔴 <strong>{{ item.nombre }}</strong> — {{ item.nivel }}</span>
            <span>Stock: {{ item.stock }} / Mínimo: {{ item.stock_minimo }}</span>
          </div>
        </div>
      </details>
    </div>

    <div class="mb-6 flex border-b border-gray-200 overflow-x-auto">
      <button @click="activeTab = 'lista'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'lista' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">📋 Lista</button>
      <button @click="activeTab = 'nuevo'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'nuevo' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">➕ Nuevo Producto</button>
      <button @click="activeTab = 'editar'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'editar' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">✏️ Editar / Agregar Nivel</button>
      <button @click="activeTab = 'compra'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'compra' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">📥 Registrar Compra</button>
    </div>

    <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm mb-10">

      <!-- ══════════════ TAB LISTA ══════════════ -->
      <div v-if="activeTab === 'lista'">
        <div class="flex justify-between items-center mb-1">
          <h2 class="text-lg font-bold text-[#FF6B2B]">Todos los Productos</h2>
          <div class="hidden md:flex gap-3 text-xs text-gray-400">
            <span>🧃 Jaba</span><span>📦 Caja</span><span>🥡 Paquete</span><span>🛍️ Bolsa</span><span>🔹 Unidad</span>
          </div>
        </div>
        <p class="text-xs text-gray-400 mb-4">🟢 stock normal · 🔴 stock crítico · ⚪ agotado</p>

        <div class="flex flex-col md:flex-row gap-4 mb-6">
          <input type="text" v-model="filtros.busqueda" placeholder="🔍 Buscar por nombre o código..."
            class="flex-1 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          <select v-model="filtros.categoria" class="w-full md:w-64 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            <option value="">— Todas las categorías —</option>
            <option v-for="cat in categorias" :key="cat.id" :value="cat.nombre">{{ cat.nombre }}</option>
          </select>
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
                <th class="pb-2 text-center">Nivel</th>
                <th class="pb-2 text-center">Contiene</th>
                <th class="pb-2 text-right">Compra</th>
                <th class="pb-2 text-right">Venta</th>
                <th class="pb-2 text-right">Margen</th>
                <th class="pb-2 text-center">Stock</th>
                <th class="pb-2 text-center">Mín.</th>
                <th class="pb-2 text-center">Estado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="(fila, idx) in filasTabla" :key="fila.productoId + '-' + (fila.nivel ? fila.nivel.id : 'x')"
                :class="['hover:bg-orange-50/50', fila.primera && idx !== 0 ? 'border-t-2 border-t-gray-200' : '']">
                <td class="py-2 text-xs text-gray-400 font-mono">{{ fila.primera ? fila.codigo : '' }}</td>
                <td class="py-2 font-bold" :class="fila.primera ? 'text-gray-800' : 'text-transparent select-none'">{{ fila.primera ? fila.nombre : '·' }}</td>
                <td class="py-2 text-sm text-gray-500">{{ fila.primera ? (fila.categoria || '—') : '' }}</td>

                <template v-if="fila.nivel">
                  <td class="py-2 text-center text-sm font-bold capitalize">{{ nivelIcono(fila.nivel.nivel) }} {{ fila.nivel.nivel }}</td>
                  <td class="py-2 text-center text-xs text-gray-400 capitalize">
                    {{ fila.nivel.contiene ? `${fila.nivel.cantidad_contenida || '?'} ${fila.nivel.contiene}(s)` : '' }}
                  </td>
                  <td class="py-2 text-right text-sm">Bs. {{ fila.nivel.precio_compra.toFixed(2) }}</td>
                  <td class="py-2 text-right font-bold">Bs. {{ fila.nivel.precio_venta.toFixed(2) }}</td>
                  <td class="py-2 text-right text-sm text-gray-500">{{ calcularMargen(fila.nivel.precio_compra, fila.nivel.precio_venta) }}%</td>
                  <td class="py-2 text-center font-bold"
                    :class="fila.nivel.stock_minimo > 0 && fila.nivel.stock <= fila.nivel.stock_minimo ? 'text-red-600' : ''">
                    {{ fila.nivel.stock }}
                  </td>
                  <td class="py-2 text-center text-sm text-gray-400">{{ fila.nivel.stock_minimo }}</td>
                  <td class="py-2 text-center text-sm">
                    <span v-if="fila.nivel.stock === 0" title="Agotado">⚪</span>
                    <span v-else-if="fila.nivel.stock_minimo > 0 && fila.nivel.stock <= fila.nivel.stock_minimo" title="Stock crítico">🔴</span>
                    <span v-else title="Stock normal">🟢</span>
                  </td>
                </template>
                <template v-else>
                  <td colspan="7" class="py-2 text-xs text-gray-400 italic">Sin niveles de venta — agrégale uno en "Editar / Agregar Nivel"</td>
                </template>
              </tr>
            </tbody>
          </table>
          <p class="text-xs text-gray-400 mt-3">Total: {{ productosFiltrados.length }} productos</p>
        </div>
      </div>

      <!-- ══════════════ TAB NUEVO PRODUCTO ══════════════ -->
      <div v-if="activeTab === 'nuevo'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Registrar Nuevo Producto</h2>

        <form @submit.prevent="guardarNuevoProducto" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">📊 Código de barras *</label>
              <input v-model="formNuevo.codigo" type="text" required class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">📝 Nombre del producto *</label>
              <input v-model="formNuevo.nombre" type="text" required class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">🏷️ Categoría</label>
              <select v-model="formNuevo.categoria_id" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                <option :value="null">— Sin categoría —</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">📄 Descripción (opcional)</label>
              <input v-model="formNuevo.descripcion" type="text" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            </div>
          </div>

          <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-4">
            <div class="flex justify-between items-center">
              <div class="text-sm font-black text-blue-700 uppercase">📦 Niveles de venta</div>
              <button type="button" @click="agregarNivelNuevo" class="text-xs bg-blue-600 hover:bg-blue-700 text-white font-bold px-3 py-1.5 rounded-lg">
                + Agregar nivel
              </button>
            </div>
            <p v-if="formNuevo.niveles.length === 0" class="text-xs text-gray-400 italic">Agrega al menos un nivel (ej: Caja, Jaba) para poder vender este producto.</p>

            <div v-for="(n, idx) in formNuevo.niveles" :key="idx" class="bg-white rounded-xl p-4 border border-blue-100 space-y-3">
              <div class="flex justify-between items-center">
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Tipo de nivel</label>
                  <select v-model="n.nivel" class="px-3 py-1.5 border rounded-lg text-sm font-bold capitalize focus:outline-none focus:border-blue-500">
                    <option value="jaba">Jaba</option>
                    <option value="caja">Caja</option>
                    <option value="paquete">Paquete</option>
                    <option value="bolsa">Bolsa</option>
                    <option value="unidad">Unidad</option>
                  </select>
                </div>
                <button type="button" @click="quitarNivelNuevo(idx)" class="text-red-500 hover:text-red-700 text-lg">🗑️</button>
              </div>

              <div v-if="opcionesContiene(n.nivel).length > 0" class="grid grid-cols-2 gap-3 bg-gray-50 p-3 rounded-lg">
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Contiene (opcional)</label>
                  <select v-model="n.contiene" class="w-full px-2 py-1.5 border rounded-lg text-sm capitalize focus:outline-none focus:border-blue-500">
                    <option :value="null">— No especificado —</option>
                    <option v-for="op in opcionesContiene(n.nivel)" :key="op" :value="op">{{ op }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Cantidad de {{ n.contiene || 'subclase' }}</label>
                  <input v-model.number="n.cantidad_contenida" type="number" min="1"
                    class="w-full px-2 py-1.5 border rounded-lg text-sm text-center focus:outline-none focus:border-blue-500">
                </div>
                <div v-if="n.contiene && n.cantidad_contenida > 0 && n.precio_compra > 0" class="col-span-2 text-xs text-blue-600">
                  💡 Costo de referencia por {{ n.contiene }}: <strong>Bs. {{ (n.precio_compra / n.cantidad_contenida).toFixed(2) }}</strong>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Precio compra (por {{ n.nivel }})</label>
                  <input v-model.number="n.precio_compra" type="number" step="0.01" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Precio venta (por {{ n.nivel }})</label>
                  <input v-model.number="n.precio_venta" type="number" step="0.01" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Stock inicial ({{ n.nivel }})</label>
                  <input v-model.number="n.stock" type="number" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Stock mínimo ({{ n.nivel }})</label>
                  <input v-model.number="n.stock_minimo" type="number" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
              </div>
            </div>
          </div>

          <button type="submit" :disabled="loading || formNuevo.niveles.length === 0"
            class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors text-lg disabled:opacity-50">
            {{ loading ? '⏳ Guardando...' : '✅ Guardar Producto' }}
          </button>
        </form>
      </div>

      <!-- ══════════════ TAB EDITAR / AGREGAR NIVEL ══════════════ -->
      <div v-if="activeTab === 'editar'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Editar Producto / Agregar Nuevo Nivel</h2>

        <div class="mb-6 space-y-3">
          <input v-model="busquedaEdicion" type="text" placeholder="🔍 Buscar por nombre o código..."
            class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          <select v-model="productoAEditarId" @change="cargarDatosEdicion"
            class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            <option :value="null">-- Selecciona un producto ({{ productosFiltradosParaEditar.length }} encontrados) --</option>
            <option v-for="p in productosFiltradosParaEditar" :key="p.id" :value="p.id">{{ p.codigo }} — {{ p.nombre }}</option>
          </select>
        </div>

        <div v-if="formEditar" class="border-t border-gray-100 pt-6 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">Nombre</label>
              <input v-model="formEditar.nombre" type="text" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">Categoría</label>
              <select v-model="formEditar.categoria_id" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                <option :value="null">— Sin categoría —</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
              </select>
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-bold text-gray-700 mb-1">Descripción</label>
              <input v-model="formEditar.descripcion" type="text" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            </div>
          </div>

          <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-3">
            <div class="text-sm font-black text-blue-700 uppercase">📦 Niveles existentes de este producto</div>

            <div v-for="n in formEditar.niveles" :key="n.id" class="bg-white rounded-xl p-3 border border-blue-100 space-y-2">
              <div class="flex justify-between items-center">
                <div class="text-sm font-bold capitalize text-gray-700">
                  {{ nivelIcono(n.nivel) }} {{ n.nivel }}
                  <span v-if="n.contiene" class="text-xs font-normal text-gray-400">(contiene {{ n.contiene }})</span>
                </div>
                <button type="button" @click="eliminarNivelExistente(n)" class="text-red-500 hover:text-red-700 text-xs font-bold px-2" title="Eliminar este nivel">
                  🗑️ Eliminar
                </button>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
                <div v-if="n.contiene">
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Cantidad de {{ n.contiene }}</label>
                  <input v-model.number="n.cantidad_contenida" type="number" min="1" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Precio compra</label>
                  <input v-model.number="n.precio_compra" type="number" step="0.01" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Precio venta</label>
                  <input v-model.number="n.precio_venta" type="number" step="0.01" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Stock actual</label>
                  <input v-model.number="n.stock" type="number" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Stock mínimo</label>
                  <input v-model.number="n.stock_minimo" type="number" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                </div>
              </div>
            </div>
            <p v-if="formEditar.niveles.length === 0" class="text-xs text-gray-400 italic">Este producto aún no tiene niveles. Agrega uno abajo.</p>
          </div>

          <div class="bg-green-50 border border-green-200 rounded-xl p-4 space-y-3">
            <div class="text-sm font-black text-green-700 uppercase">➕ Agregar nuevo nivel a este producto</div>

            <div class="bg-white rounded-xl p-4 border border-green-100 space-y-3">
              <div>
                <label class="block text-[10px] font-bold text-gray-500 mb-1">Tipo de nivel</label>
                <select v-model="nuevoNivelEditar.nivel" class="px-3 py-1.5 border rounded-lg text-sm font-bold capitalize focus:outline-none focus:border-green-500">
                  <option value="jaba">Jaba</option>
                  <option value="caja">Caja</option>
                  <option value="paquete">Paquete</option>
                  <option value="bolsa">Bolsa</option>
                  <option value="unidad">Unidad</option>
                </select>
              </div>

              <div v-if="opcionesContiene(nuevoNivelEditar.nivel).length > 0" class="grid grid-cols-2 gap-3 bg-gray-50 p-3 rounded-lg">
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Contiene (opcional)</label>
                  <select v-model="nuevoNivelEditar.contiene" class="w-full px-2 py-1.5 border rounded-lg text-sm capitalize focus:outline-none focus:border-green-500">
                    <option :value="null">— No especificado —</option>
                    <option v-for="op in opcionesContiene(nuevoNivelEditar.nivel)" :key="op" :value="op">{{ op }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Cantidad de {{ nuevoNivelEditar.contiene || 'subclase' }}</label>
                  <input v-model.number="nuevoNivelEditar.cantidad_contenida" type="number" min="1" class="w-full px-2 py-1.5 border rounded-lg text-sm text-center focus:outline-none focus:border-green-500">
                </div>
                <div v-if="nuevoNivelEditar.contiene && nuevoNivelEditar.cantidad_contenida > 0 && nuevoNivelEditar.precio_compra > 0" class="col-span-2 text-xs text-green-700">
                  💡 Costo de referencia por {{ nuevoNivelEditar.contiene }}: <strong>Bs. {{ (nuevoNivelEditar.precio_compra / nuevoNivelEditar.cantidad_contenida).toFixed(2) }}</strong>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Precio compra</label>
                  <input v-model.number="nuevoNivelEditar.precio_compra" type="number" step="0.01" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-green-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Precio venta</label>
                  <input v-model.number="nuevoNivelEditar.precio_venta" type="number" step="0.01" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-green-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Stock inicial</label>
                  <input v-model.number="nuevoNivelEditar.stock" type="number" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-green-500">
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-500 mb-1">Stock mínimo</label>
                  <input v-model.number="nuevoNivelEditar.stock_minimo" type="number" min="0" class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-green-500">
                </div>
              </div>
              <button type="button" @click="agregarNivelAProductoExistente"
                class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 rounded-lg text-sm">
                + Agregar este nivel al producto
              </button>
            </div>
          </div>

          <button @click="actualizarProducto" :disabled="loading"
            class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors disabled:opacity-50">
            {{ loading ? '⏳ Guardando...' : '💾 Guardar todos los cambios' }}
          </button>
        </div>

        <div v-else class="text-center py-8 text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
          Selecciona un producto para editarlo o agregarle un nivel nuevo.
        </div>
      </div>

      <!-- ══════════════ TAB REGISTRAR COMPRA ══════════════ -->
      <div v-if="activeTab === 'compra'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-1">📥 Registrar Compra</h2>
        <p class="text-sm text-gray-500 mb-6">Indica en qué nivel recibiste la mercadería.</p>

        <div class="mb-6 bg-gray-50 p-4 rounded-xl border border-gray-200">
          <label class="block text-sm font-bold text-gray-700 mb-1">🏭 Proveedor</label>
          <select v-model="proveedorId" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            <option :value="null">— Sin proveedor especificado —</option>
            <option v-for="p in proveedores" :key="p.id" :value="p.id">{{ p.nombre }}</option>
          </select>
        </div>

        <div class="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-4 space-y-3">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">📊 Producto</label>
            <select v-model="compraTemp.productoId" @change="compraTemp.nivelId = null"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              <option :value="null">-- Seleccionar producto --</option>
              <option v-for="p in productos" :key="p.id" :value="p.id">{{ p.codigo }} — {{ p.nombre }}</option>
            </select>
          </div>
          <div v-if="productoSeleccionadoCompra">
            <label class="block text-sm font-bold text-gray-700 mb-2">📦 Nivel recibido</label>
            <select v-model="compraTemp.nivelId" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              <option :value="null">-- Seleccionar nivel --</option>
              <option v-for="n in productoSeleccionadoCompra.niveles" :key="n.id" :value="n.id" class="capitalize">
                {{ n.nivel }} (stock actual: {{ n.stock }})
              </option>
            </select>
          </div>
        </div>

        <div v-if="compraTemp.nivelId" class="mb-6 bg-white border border-gray-200 rounded-xl p-5 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">Cantidad</label>
              <input v-model.number="compraTemp.cantidad" type="number" min="1"
                class="w-full px-4 py-3 rounded-xl border-2 border-gray-300 focus:outline-none focus:border-[#FF6B2B] text-center font-black text-xl">
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">Precio compra (Bs.)</label>
              <input v-model.number="compraTemp.precio" type="number" step="0.01" min="0"
                class="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            </div>
          </div>
          <div class="bg-gray-700 text-white rounded-xl p-3 flex justify-between items-center">
            <span class="font-bold">Subtotal</span>
            <span class="font-black text-xl">Bs. {{ (compraTemp.cantidad * compraTemp.precio).toFixed(2) }}</span>
          </div>
          <button @click="agregarAlCarritoCompra" class="w-full bg-gray-800 hover:bg-black text-white font-bold py-3 rounded-xl">
            ➕ Agregar al carrito
          </button>
        </div>

        <div v-if="carritoCompra.length > 0">
          <h3 class="font-bold text-gray-700 mb-3">🛒 Carrito de Compra</h3>
          <div class="border border-gray-200 rounded-xl overflow-hidden mb-4">
            <div v-for="(item, index) in carritoCompra" :key="index" class="flex items-center justify-between p-3 border-b border-gray-100 last:border-0 hover:bg-gray-50">
              <div class="flex-1">
                <div class="font-medium text-sm">{{ item.nombre }}</div>
                <div class="text-xs text-gray-400 capitalize">{{ item.cantidad }} {{ item.nivelNombre }}(s) × Bs. {{ item.precio_unitario.toFixed(2) }}</div>
              </div>
              <div class="w-32 text-right font-bold">Bs. {{ item.subtotal.toFixed(2) }}</div>
              <button @click="carritoCompra.splice(index, 1)" class="text-red-500 hover:text-red-700 font-bold px-2">🗑️</button>
            </div>
          </div>
          <div class="text-right text-xl font-black mb-6">Total: Bs. {{ totalCarritoCompra.toFixed(2) }}</div>
          <input v-model="notasCompra" type="text" placeholder="Notas (factura, referencia...)"
            class="w-full px-4 py-2 mb-6 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          <div class="flex gap-4">
            <button @click="registrarCompra" :disabled="loading" class="flex-1 bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg disabled:opacity-50">
              {{ loading ? '⏳ Registrando...' : '✅ Registrar Compra' }}
            </button>
            <button @click="carritoCompra = []" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-lg">🗑️ Limpiar</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import inventarioService from '@/services/inventarioService'

const activeTab = ref('lista')
const loading = ref(false)
const error = ref(null)
const categorias = ref([])
const productos = ref([])
const proveedores = ref([])
const proveedorId = ref(null)

onMounted(async () => { await cargarDatos() })

const cargarDatos = async () => {
  loading.value = true
  error.value = null
  try {
    const [prods, cats, provs] = await Promise.all([
      inventarioService.getProductos(),
      inventarioService.getCategorias(),
      inventarioService.getProveedores()
    ])
    productos.value = prods
    categorias.value = cats
    proveedores.value = provs.filter(p => p.activo)
  } catch (e) {
    error.value = 'Error al cargar datos.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

const opcionesContiene = (nivel) => {
  if (nivel === 'jaba') return ['caja', 'paquete', 'bolsa']
  if (nivel === 'caja') return ['paquete', 'bolsa', 'caja']
  return []
}

const nivelIcono = (nivel) => ({
  jaba: '🧃', caja: '📦', paquete: '🥡', bolsa: '🛍️', unidad: '🔹'
}[nivel] || '📦')

const calcularMargen = (compra, venta) => {
  if (!compra || compra === 0) return 100.0
  return (((venta - compra) / compra) * 100).toFixed(1)
}

// ── FILTROS / LISTA ─────────────────────────────────────────────
const filtros = ref({ busqueda: '', categoria: '' })
const productosFiltrados = computed(() =>
  productos.value.filter(p => {
    const coincideBusqueda = p.nombre.toLowerCase().includes(filtros.value.busqueda.toLowerCase()) || p.codigo.includes(filtros.value.busqueda)
    const coincideCategoria = filtros.value.categoria === '' || p.categoria === filtros.value.categoria
    return coincideBusqueda && coincideCategoria
  })
)

const filasTabla = computed(() => {
  const filas = []
  productosFiltrados.value.forEach(p => {
    const niveles = (p.niveles && p.niveles.length > 0) ? p.niveles : [null]
    niveles.forEach((n, i) => {
      filas.push({ productoId: p.id, primera: i === 0, codigo: p.codigo, nombre: p.nombre, categoria: p.categoria, nivel: n })
    })
  })
  return filas
})

const stockCritico = computed(() => {
  const items = []
  productos.value.forEach(p => {
    ;(p.niveles || []).forEach(n => {
      if (n.stock_minimo > 0 && n.stock <= n.stock_minimo) {
        items.push({ nombre: p.nombre, nivel: n.nivel, stock: n.stock, stock_minimo: n.stock_minimo })
      }
    })
  })
  return items
})

// ── NUEVO PRODUCTO ────────────────────────────────────────────────
const nivelVacio = () => ({ nivel: 'caja', contiene: null, cantidad_contenida: null, precio_compra: 0, precio_venta: 0, stock: 0, stock_minimo: 0 })

const formNuevo = ref({ codigo: '', nombre: '', categoria_id: null, descripcion: '', niveles: [nivelVacio()] })

const agregarNivelNuevo = () => formNuevo.value.niveles.push(nivelVacio())
const quitarNivelNuevo = (idx) => formNuevo.value.niveles.splice(idx, 1)

const guardarNuevoProducto = async () => {
  loading.value = true
  try {
    await inventarioService.crearProducto(formNuevo.value)
    alert(`✅ Producto "${formNuevo.value.nombre}" guardado con ${formNuevo.value.niveles.length} nivel(es).`)
    formNuevo.value = { codigo: '', nombre: '', categoria_id: null, descripcion: '', niveles: [nivelVacio()] }
    await cargarDatos()
    activeTab.value = 'lista'
  } catch (e) {
    alert('❌ Error al guardar: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

// ── EDITAR / AGREGAR NIVEL ──────────────────────────────────────
const productoAEditarId = ref(null)
const formEditar = ref(null)
const busquedaEdicion = ref('')
const nuevoNivelEditar = ref(nivelVacio())

const productosFiltradosParaEditar = computed(() => {
  const term = busquedaEdicion.value.toLowerCase()
  return productos.value.filter(p => p.nombre.toLowerCase().includes(term) || p.codigo.toLowerCase().includes(term))
})

const cargarDatosEdicion = () => {
  if (!productoAEditarId.value) { formEditar.value = null; return }
  const prod = productos.value.find(p => p.id === productoAEditarId.value)
  if (prod) formEditar.value = { ...prod, niveles: JSON.parse(JSON.stringify(prod.niveles || [])) }
  nuevoNivelEditar.value = nivelVacio()
}

const actualizarProducto = async () => {
  loading.value = true
  try {
    await inventarioService.actualizarProducto(formEditar.value.id, {
      nombre: formEditar.value.nombre,
      categoria_id: formEditar.value.categoria_id,
      descripcion: formEditar.value.descripcion
    })
    await Promise.all(formEditar.value.niveles.map(n => inventarioService.editarNivel(n.id, {
      contiene: n.contiene, cantidad_contenida: n.cantidad_contenida,
      precio_compra: n.precio_compra, precio_venta: n.precio_venta,
      stock: n.stock, stock_minimo: n.stock_minimo
    })))
    alert(`✅ "${formEditar.value.nombre}" actualizado`)
    await cargarDatos()
    cargarDatosEdicion()
  } catch (e) {
    alert('❌ Error al actualizar: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

const agregarNivelAProductoExistente = async () => {
  try {
    await inventarioService.agregarNivel(formEditar.value.id, nuevoNivelEditar.value)
    alert(`✅ Nivel "${nuevoNivelEditar.value.nivel}" agregado`)
    nuevoNivelEditar.value = nivelVacio()
    await cargarDatos()
    cargarDatosEdicion()
  } catch (e) {
    alert('❌ Error al agregar nivel: ' + (e.response?.data?.detail || e.message))
  }
}

const eliminarNivelExistente = async (nivel) => {
  if (!confirm(`¿Eliminar el nivel "${nivel.nivel}" de "${formEditar.value.nombre}"? No se puede deshacer.`)) return
  try {
    await inventarioService.eliminarNivel(nivel.id)
    await cargarDatos()
    cargarDatosEdicion()
  } catch (e) {
    alert('❌ Error al eliminar nivel: ' + (e.response?.data?.detail || e.message))
  }
}

// ── COMPRAS ───────────────────────────────────────────────────────
const compraTemp = ref({ productoId: null, nivelId: null, cantidad: 1, precio: 0 })
const carritoCompra = ref([])
const notasCompra = ref('')

const productoSeleccionadoCompra = computed(() => productos.value.find(p => p.id === compraTemp.value.productoId) || null)

const agregarAlCarritoCompra = () => {
  const prod = productoSeleccionadoCompra.value
  const nivel = prod?.niveles.find(n => n.id === compraTemp.value.nivelId)
  if (!prod || !nivel || compraTemp.value.cantidad <= 0) return

  carritoCompra.value.push({
    nivelId: nivel.id, nombre: prod.nombre, nivelNombre: nivel.nivel,
    cantidad: compraTemp.value.cantidad, precio_unitario: compraTemp.value.precio,
    subtotal: compraTemp.value.cantidad * compraTemp.value.precio
  })
  compraTemp.value = { productoId: null, nivelId: null, cantidad: 1, precio: 0 }
}

const totalCarritoCompra = computed(() => carritoCompra.value.reduce((acc, i) => acc + i.subtotal, 0))

const registrarCompra = async () => {
  loading.value = true
  try {
    const items = carritoCompra.value.map(i => ({ nivel_id: i.nivelId, cantidad: i.cantidad, precio_unitario: i.precio_unitario, subtotal: i.subtotal }))
    const result = await inventarioService.registrarCompra(items, notasCompra.value, proveedorId.value)
    alert(`✅ Compra ${result.numero_compra} registrada por Bs. ${result.total.toFixed(2)}`)
    carritoCompra.value = []
    notasCompra.value = ''
    proveedorId.value = null
    await cargarDatos()
  } catch (e) {
    alert('❌ Error al registrar compra: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
</script>