<template>
  <div class="p-8 pl-10 max-w-full">
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
          <div v-for="p in stockCritico" :key="p.id"
            class="bg-[#3a1e1e] border-l-4 border-red-500 text-white p-2 px-4 rounded text-sm flex justify-between">
            <span>🔴 <strong>{{ p.nombre }}</strong></span>
            <span>Stock: {{ p.stock }} / Mínimo: {{ p.stock_minimo }}</span>
          </div>
        </div>
      </details>
    </div>

    <div class="mb-6 flex border-b border-gray-200 overflow-x-auto">
      <button @click="activeTab = 'lista'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'lista' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">📋 Lista de Productos</button>
      <button @click="activeTab = 'nuevo'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'nuevo' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">➕ Nuevo Producto</button>
      <button @click="activeTab = 'editar'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'editar' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">✏️ Editar Producto</button>
      <button @click="activeTab = 'compra'" :class="['whitespace-nowrap py-3 px-6 font-bold text-sm transition-colors', activeTab === 'compra' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">📥 Registrar Compra</button>
    </div>

    <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm mb-10">

      <!-- ══════════════════════════════════════════════
           TAB LISTA
      ══════════════════════════════════════════════ -->
      <div v-if="activeTab === 'lista'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Todos los Productos</h2>
        <div class="flex flex-col md:flex-row gap-4 mb-6">
          <div class="flex-1">
            <input type="text" v-model="filtros.busqueda" placeholder="🔍 Buscar por nombre o código..."
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div class="w-full md:w-64">
            <select v-model="filtros.categoria"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              <option value="">— Todas las categorías —</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.nombre">{{ cat.nombre }}</option>
            </select>
          </div>
        </div>

        <div v-if="productosFiltrados.length === 0"
          class="text-center py-8 text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
          No se encontraron productos.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-gray-100 text-sm text-gray-500">
                <th class="pb-2">Código</th>
                <th class="pb-2">Nombre</th>
                <th class="pb-2">Categoría</th>
                <th class="pb-2 text-right">Compra/Ud</th>
                <th class="pb-2 text-right">Venta/Ud</th>
                <th class="pb-2 text-right">Margen</th>
                <th class="pb-2 text-center">Stock</th>
                <th class="pb-2 text-center">Mín.</th>
                <th class="pb-2">Presentaciones</th>
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
                <td class="py-3 text-xs text-blue-600">{{ resumenPresentaciones(p) }}</td>
                <td class="py-3 text-center text-sm">
                  <span v-if="p.stock > p.stock_minimo">✅</span>
                  <span v-else>⚠️</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p class="text-xs text-gray-400 mt-3">Total: {{ productosFiltrados.length }} productos</p>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════
           TAB NUEVO PRODUCTO
      ══════════════════════════════════════════════ -->
      <div v-if="activeTab === 'nuevo'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Registrar Nuevo Producto</h2>

        <form @submit.prevent="guardarNuevoProducto" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

            <!-- Columna izquierda -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📊 Código de barras *</label>
                <input v-model="formNuevo.codigo" type="text" required placeholder="Ej: 7500123456789"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📝 Nombre del producto *</label>
                <input v-model="formNuevo.nombre" type="text" required placeholder="Ej: Coca Cola 2.5L"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">🏷️ Categoría</label>
                <select v-model="formNuevo.categoria_id"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  <option :value="null">— Sin categoría —</option>
                  <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📐 Unidad base (descriptiva)</label>
                <select v-model="formNuevo.unidad"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  <option value="unidad">unidad</option>
                  <option value="kg">kg</option>
                  <option value="litro">litro</option>
                  <option value="gramo">gramo</option>
                  <option value="bolsa">bolsa</option>
                  <option value="docena">docena</option>
                </select>
                <p class="text-xs text-gray-400 mt-1">Es solo la etiqueta de la unidad más pequeña. Las presentaciones al por mayor (Jaba, Caja, etc.) se agregan abajo.</p>
              </div>

              <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div class="text-xs font-bold text-gray-500 uppercase mb-3">💰 Precios por unidad base</div>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Precio de compra (Bs.)</label>
                    <input v-model.number="formNuevo.precio_compra" type="number" step="0.01" min="0"
                      class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Precio de venta (Bs.) *</label>
                    <input v-model.number="formNuevo.precio_venta" type="number" step="0.01" min="0" required
                      class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📄 Descripción (opcional)</label>
                <textarea v-model="formNuevo.descripcion" rows="2"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]"></textarea>
              </div>
            </div>

            <!-- Columna derecha -->
            <div class="space-y-4">

              <!-- ✅ PRESENTACIONES — siempre disponible, para cualquier producto -->
              <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-3">
                <div class="flex justify-between items-center">
                  <div class="text-xs font-black text-blue-700 uppercase tracking-wide">
                    📦 Presentaciones al por mayor (opcional)
                  </div>
                  <button type="button" @click="agregarPresentacionNuevo"
                    class="text-xs bg-blue-600 hover:bg-blue-700 text-white font-bold px-3 py-1 rounded-lg">
                    + Agregar (Jaba, Caja, Paquete...)
                  </button>
                </div>

                <p v-if="formNuevo.presentaciones.length === 0" class="text-xs text-gray-400 italic">
                  Sin presentaciones — el producto se venderá solo por unidad.
                </p>

                <div v-for="(pres, idx) in formNuevo.presentaciones" :key="idx"
                  class="bg-white rounded-lg p-3 border border-blue-100 grid grid-cols-12 gap-2 items-end">
                  <div class="col-span-4">
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">Nombre</label>
                    <input v-model="pres.nombre" type="text" placeholder="Ej: Jaba"
                      class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                  </div>
                  <div class="col-span-3">
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">Equivale a (uds.)</label>
                    <input v-model.number="pres.unidades_base" type="number" min="1"
                      class="w-full px-2 py-1.5 border rounded-lg text-sm text-center focus:outline-none focus:border-blue-500">
                  </div>
                  <div class="col-span-2">
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">P. compra</label>
                    <input v-model.number="pres.precio_compra" type="number" min="0" step="0.5"
                      class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                  </div>
                  <div class="col-span-2">
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">P. venta</label>
                    <input v-model.number="pres.precio_venta" type="number" min="0" step="0.5"
                      class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                  </div>
                  <div class="col-span-1 text-center">
                    <button type="button" @click="quitarPresentacionNuevo(idx)" class="text-red-500 hover:text-red-700 text-lg">🗑️</button>
                  </div>

                  <div v-if="pres.unidades_base > 0 && pres.precio_venta > 0" class="col-span-12 text-[11px] text-blue-600">
                    ≈ Bs. {{ (pres.precio_venta / pres.unidades_base).toFixed(2) }}/unidad al vender por {{ pres.nombre || 'esta presentación' }}
                    <span class="text-gray-400">(precio suelto: Bs. {{ (formNuevo.precio_venta || 0).toFixed(2) }}/unidad)</span>
                  </div>
                </div>
              </div>

              <!-- Stock: calculado si hay presentaciones, manual si no -->
              <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div class="text-xs font-bold text-gray-500 uppercase mb-3">📦 Stock inicial</div>

                <div v-if="formNuevo.presentaciones.length > 0" class="space-y-2">
                  <div class="grid grid-cols-3 gap-3">
                    <div>
                      <label class="block text-xs font-bold text-gray-600 mb-1">Recibido en</label>
                      <select v-model="stockHelperNuevo.presentacionIdx"
                        class="w-full px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm">
                        <option v-for="(p, i) in formNuevo.presentaciones" :key="i" :value="i">{{ p.nombre || '—' }}</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-gray-600 mb-1">Cantidad</label>
                      <input v-model.number="stockHelperNuevo.cantidad" type="number" min="0"
                        class="w-full px-3 py-2 rounded-lg border border-gray-200 bg-white text-center font-bold">
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-gray-600 mb-1">+ Sueltas</label>
                      <input v-model.number="stockHelperNuevo.sueltas" type="number" min="0"
                        class="w-full px-3 py-2 rounded-lg border border-gray-200 bg-white text-center">
                    </div>
                  </div>
                  <div class="bg-white rounded-lg p-2 border border-gray-100 flex justify-between items-center">
                    <span class="text-xs text-gray-500">Total calculado</span>
                    <span class="font-black text-blue-700">{{ formNuevo.stock }} unidades</span>
                  </div>
                </div>

                <div v-else>
                  <label class="block text-xs font-bold text-gray-600 mb-1">Stock inicial (unidades)</label>
                  <input v-model.number="formNuevo.stock" type="number" step="1" min="0"
                    class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                </div>
              </div>

              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">⚠️ Stock mínimo (unidades)</label>
                <input v-model.number="formNuevo.stock_minimo" type="number" step="1" min="0"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
            </div>
          </div>

          <!-- Preview margen -->
          <div v-if="formNuevo.precio_compra > 0 && formNuevo.precio_venta > 0"
            class="bg-green-50 border border-green-200 p-4 rounded-xl grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div class="text-center">
              <div class="text-xs text-gray-400 mb-1">Costo/unidad</div>
              <div class="font-black text-gray-800">Bs. {{ formNuevo.precio_compra.toFixed(2) }}</div>
            </div>
            <div class="text-center">
              <div class="text-xs text-gray-400 mb-1">Precio venta</div>
              <div class="font-black text-[#FF6B2B]">Bs. {{ formNuevo.precio_venta.toFixed(2) }}</div>
            </div>
            <div class="text-center">
              <div class="text-xs text-gray-400 mb-1">Ganancia/unidad</div>
              <div class="font-black text-green-600">Bs. {{ (formNuevo.precio_venta - formNuevo.precio_compra).toFixed(2) }}</div>
            </div>
            <div class="text-center">
              <div class="text-xs text-gray-400 mb-1">Margen</div>
              <div class="font-black text-green-600">{{ calcularMargen(formNuevo.precio_compra, formNuevo.precio_venta) }}%</div>
            </div>
          </div>

          <button type="submit" :disabled="loading"
            class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors text-lg disabled:opacity-50">
            {{ loading ? '⏳ Guardando...' : '✅ Guardar Producto' }}
          </button>
        </form>
      </div>

      <!-- ══════════════════════════════════════════════
           TAB EDITAR PRODUCTO
      ══════════════════════════════════════════════ -->
      <div v-if="activeTab === 'editar'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-4">Editar Producto Existente</h2>

        <div class="mb-6 space-y-3">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">🔍 Buscar producto para editar</label>
            <input v-model="busquedaEdicion" type="text" placeholder="Escribe el nombre o código..."
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>
          <div>
            <select v-model="productoAEditarId" @change="cargarDatosEdicion"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              <option :value="null">-- Selecciona de la lista ({{ productosFiltradosParaEditar.length }} encontrados) --</option>
              <option v-for="p in productosFiltradosParaEditar" :key="p.id" :value="p.id">
                {{ p.codigo }} — {{ p.nombre }} ({{ p.unidad }})
              </option>
            </select>
          </div>
        </div>

        <div v-if="formEditar" class="border-t border-gray-100 pt-6">
          <form @submit.prevent="actualizarProducto" class="grid grid-cols-1 md:grid-cols-2 gap-6">

            <!-- Columna izquierda -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Nombre</label>
                <input v-model="formEditar.nombre" type="text" required
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Categoría</label>
                <select v-model="formEditar.categoria_id"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  <option :value="null">— Sin categoría —</option>
                  <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📐 Unidad base (descriptiva)</label>
                <select v-model="formEditar.unidad"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  <option value="unidad">unidad</option>
                  <option value="kg">kg</option>
                  <option value="litro">litro</option>
                  <option value="gramo">gramo</option>
                  <option value="bolsa">bolsa</option>
                  <option value="docena">docena</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📦 Stock actual (unidades)</label>
                <input v-model.number="formEditar.stock" type="number" step="1" min="0"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">⚠️ Stock mínimo (unidades)</label>
                <input v-model.number="formEditar.stock_minimo" type="number" step="1" min="0"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>

              <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div class="text-xs font-bold text-gray-500 uppercase mb-3">💰 Precios por unidad base</div>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Precio de compra (Bs.)</label>
                    <input v-model.number="formEditar.precio_compra" type="number" step="0.01" min="0"
                      class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Precio de venta (Bs.)</label>
                    <input v-model.number="formEditar.precio_venta" type="number" step="0.01" min="0"
                      class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  </div>
                </div>
              </div>

              <!-- Preview margen -->
              <div v-if="formEditar.precio_compra > 0 && formEditar.precio_venta > 0"
                class="bg-green-50 border border-green-200 rounded-xl p-3 grid grid-cols-3 gap-2 text-center">
                <div>
                  <div class="text-[10px] text-gray-400 uppercase mb-1">Costo unit.</div>
                  <div class="font-black text-gray-700 text-sm">Bs. {{ formEditar.precio_compra.toFixed(2) }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-400 uppercase mb-1">Ganancia</div>
                  <div class="font-black text-green-600 text-sm">
                    Bs. {{ (formEditar.precio_venta - formEditar.precio_compra).toFixed(2) }}
                  </div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-400 uppercase mb-1">Margen</div>
                  <div class="font-black text-green-600 text-sm">
                    {{ calcularMargen(formEditar.precio_compra, formEditar.precio_venta) }}%
                  </div>
                </div>
              </div>
            </div>

            <!-- Columna derecha: Presentaciones -->
            <div class="space-y-4">
              <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-3">
                <div class="flex justify-between items-center">
                  <div class="text-xs font-black text-blue-700 uppercase tracking-wide">
                    📦 Presentaciones al por mayor
                  </div>
                  <button type="button" @click="agregarPresentacionEditar"
                    class="text-xs bg-blue-600 hover:bg-blue-700 text-white font-bold px-3 py-1 rounded-lg">
                    + Agregar
                  </button>
                </div>

                <p v-if="formEditar.presentaciones.length === 0" class="text-xs text-gray-400 italic">
                  Este producto no tiene presentaciones al por mayor. Se vende solo por unidad.
                </p>

                <div v-for="(pres, idx) in formEditar.presentaciones" :key="idx"
                  class="bg-white rounded-lg p-3 border border-blue-100 grid grid-cols-12 gap-2 items-end">
                  <div class="col-span-4">
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">Nombre</label>
                    <input v-model="pres.nombre" type="text" placeholder="Ej: Jaba"
                      class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                  </div>
                  <div class="col-span-3">
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">Equivale a (uds.)</label>
                    <input v-model.number="pres.unidades_base" type="number" min="1"
                      class="w-full px-2 py-1.5 border rounded-lg text-sm text-center focus:outline-none focus:border-blue-500">
                  </div>
                  <div class="col-span-2">
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">P. compra</label>
                    <input v-model.number="pres.precio_compra" type="number" min="0" step="0.5"
                      class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                  </div>
                  <div class="col-span-2">
                    <label class="block text-[10px] font-bold text-gray-500 mb-1">P. venta</label>
                    <input v-model.number="pres.precio_venta" type="number" min="0" step="0.5"
                      class="w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:border-blue-500">
                  </div>
                  <div class="col-span-1 text-center">
                    <button type="button" @click="quitarPresentacionEditar(idx)" class="text-red-500 hover:text-red-700 text-lg">🗑️</button>
                  </div>

                  <div v-if="pres.unidades_base > 0 && pres.precio_venta > 0" class="col-span-12 text-[11px] text-blue-600">
                    ≈ Bs. {{ (pres.precio_venta / pres.unidades_base).toFixed(2) }}/unidad vendiendo por {{ pres.nombre || 'esta presentación' }}
                  </div>
                </div>
              </div>
            </div>

            <div class="md:col-span-2">
              <button type="submit" :disabled="loading"
                class="w-full bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors disabled:opacity-50">
                {{ loading ? '⏳ Actualizando...' : '💾 Actualizar Producto' }}
              </button>
            </div>
          </form>
        </div>

        <div v-else class="text-center py-8 text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
          Selecciona un producto de la lista para editar sus detalles.
        </div>
      </div>

      <!-- ══════════════════════════════════════════════
           TAB REGISTRAR COMPRA
      ══════════════════════════════════════════════ -->
      <div v-if="activeTab === 'compra'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-1">📥 Registrar Compra / Ingreso de Mercadería</h2>
        <p class="text-sm text-gray-500 mb-6">Agrega productos al carrito para actualizar el stock.</p>

        <!-- Proveedor -->
        <div class="mb-6 bg-gray-50 p-4 rounded-xl border border-gray-200">
          <label class="block text-sm font-bold text-gray-700 mb-1">🏭 Proveedor</label>
          <select v-model="proveedorId"
            class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            <option :value="null">— Sin proveedor especificado —</option>
            <option v-for="p in proveedores" :key="p.id" :value="p.id">
              {{ p.nombre }}{{ p.contacto ? ` · ${p.contacto}` : '' }}
            </option>
          </select>
          <p class="text-xs text-gray-400 mt-2">
            ¿No está el proveedor?
            <router-link to="/proveedores" class="text-[#FF6B2B] font-bold hover:underline">Regístralo aquí →</router-link>
          </p>
        </div>

        <!-- Selector de producto -->
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-4">
          <label class="block text-sm font-bold text-gray-700 mb-2">📊 Seleccionar producto</label>
          <select v-model="compraTemp.productoId"
            class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
            <option :value="null">-- Seleccionar producto --</option>
            <option v-for="p in productos" :key="p.id" :value="p.id">
              {{ p.codigo }} — {{ p.nombre }}
            </option>
          </select>
        </div>

        <div v-if="compraTemp.productoId" class="mb-6">

          <!-- Selector de presentación recibida -->
          <div v-if="tienePresentacionesCompra" class="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-4">
            <label class="block text-sm font-bold text-gray-700 mb-1">📦 Recibido en</label>
            <select v-model="compraTemp.presentacionIdx"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              <option :value="null">Unidad suelta</option>
              <option v-for="(pres, i) in productoSeleccionadoCompra.presentaciones" :key="i" :value="i">
                {{ pres.nombre }} ({{ pres.unidades_base }} uds.)
              </option>
            </select>
          </div>

          <!-- ✅ RECIBIDO POR PRESENTACIÓN (Jaba/Caja/etc.) -->
          <div v-if="compraTemp.presentacionIdx !== null" class="bg-blue-50 border border-blue-200 rounded-xl p-5 space-y-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-lg">📦</span>
              <div>
                <div class="font-black text-blue-800">{{ productoSeleccionadoCompra.nombre }}</div>
                <div class="text-xs text-blue-600">
                  {{ presentacionSeleccionadaCompra.unidades_base }} unidades por {{ presentacionSeleccionadaCompra.nombre }}
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">
                  N° de {{ presentacionSeleccionadaCompra.nombre }}
                </label>
                <input v-model.number="compraTemp.cantidadPresentacion" type="number" min="0" step="1"
                  class="w-full px-4 py-3 rounded-xl border-2 border-blue-300 focus:outline-none focus:border-blue-500 bg-white text-center font-black text-xl">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Unidades sueltas (opcional)</label>
                <input v-model.number="compraTemp.unidadesSueltas" type="number" min="0" step="1"
                  class="w-full px-4 py-3 rounded-xl border-2 border-blue-200 focus:outline-none focus:border-blue-400 bg-white text-center font-bold text-xl">
              </div>
            </div>

            <div class="bg-white rounded-xl p-3 border border-blue-200">
              <div class="flex justify-between items-center text-sm">
                <span class="text-gray-500">
                  {{ compraTemp.cantidadPresentacion || 0 }} × {{ presentacionSeleccionadaCompra.unidades_base }} + {{ compraTemp.unidadesSueltas || 0 }} sueltas
                </span>
                <span class="font-black text-blue-700 text-lg">= {{ compraTemp.cantidad }} unidades</span>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-600 mb-1">
                Precio compra por unidad base (Bs.) — editable si cambió
              </label>
              <input v-model.number="compraTemp.precio" type="number" step="0.01" min="0"
                class="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:border-blue-500 bg-white">
            </div>

            <div class="bg-blue-700 text-white rounded-xl p-3 flex justify-between items-center">
              <span class="font-bold">Subtotal de esta entrada</span>
              <span class="font-black text-xl">Bs. {{ (compraTemp.cantidad * compraTemp.precio).toFixed(2) }}</span>
            </div>

            <button @click="agregarAlCarritoCompra" :disabled="!compraTemp.cantidad || compraTemp.cantidad <= 0"
              class="w-full bg-gray-800 hover:bg-black text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50">
              ➕ Agregar {{ compraTemp.cantidad }} unidades al carrito
            </button>
          </div>

          <!-- ✅ RECIBIDO SUELTO -->
          <div v-else class="bg-gray-50 border border-gray-200 rounded-xl p-5 space-y-4">
            <div class="flex items-center gap-2 mb-2">
              <div>
                <div class="font-black text-gray-800">{{ productoSeleccionadoCompra.nombre }}</div>
                <div class="text-xs text-gray-500">Por {{ productoSeleccionadoCompra.unidad }}</div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Cantidad ({{ productoSeleccionadoCompra.unidad }})</label>
                <input v-model.number="compraTemp.cantidad" type="number" min="1" step="1"
                  class="w-full px-4 py-3 rounded-xl border-2 border-gray-300 focus:outline-none focus:border-[#FF6B2B] bg-white text-center font-black text-xl">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Precio compra por unidad (Bs.)</label>
                <input v-model.number="compraTemp.precio" type="number" step="0.01" min="0"
                  class="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:outline-none focus:border-[#FF6B2B] bg-white">
              </div>
            </div>

            <div class="bg-gray-700 text-white rounded-xl p-3 flex justify-between items-center">
              <span class="font-bold">Subtotal</span>
              <span class="font-black text-xl">Bs. {{ (compraTemp.cantidad * compraTemp.precio).toFixed(2) }}</span>
            </div>

            <button @click="agregarAlCarritoCompra" :disabled="!compraTemp.cantidad || compraTemp.cantidad <= 0"
              class="w-full bg-gray-800 hover:bg-black text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50">
              ➕ Agregar al carrito
            </button>
          </div>
        </div>

        <div v-else class="mb-6 text-center py-6 text-gray-400 bg-gray-50 rounded-xl border border-gray-200">
          Selecciona un producto arriba para ver las opciones de entrada
        </div>

        <!-- Carrito -->
        <div v-if="carritoCompra.length > 0">
          <div v-if="proveedorId" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700 font-bold">
            🏭 Proveedor: {{ proveedores.find(p => p.id === proveedorId)?.nombre }}
          </div>
          <div v-else class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-700">
            ⚠️ Sin proveedor asignado
          </div>

          <h3 class="font-bold text-gray-700 mb-3">🛒 Carrito de Compra</h3>
          <div class="border border-gray-200 rounded-xl overflow-hidden mb-4">
            <div v-for="(item, index) in carritoCompra" :key="index"
              class="flex items-center justify-between p-3 border-b border-gray-100 last:border-0 hover:bg-gray-50">
              <div class="flex-1">
                <div class="font-medium text-sm">{{ item.nombre }}</div>
                <div class="text-xs text-gray-400">
                  <span v-if="item.presentacion_nombre">{{ item.presentacion_cantidad }} {{ item.presentacion_nombre }}(s) · </span>
                  {{ item.cantidad }} unid. × Bs. {{ item.precio_unitario.toFixed(2) }}
                </div>
              </div>
              <div class="w-32 text-right font-bold">Bs. {{ item.subtotal.toFixed(2) }}</div>
              <div class="w-16 text-right">
                <button @click="eliminarDelCarritoCompra(index)" class="text-red-500 hover:text-red-700 font-bold px-2">🗑️</button>
              </div>
            </div>
          </div>

          <div class="text-right text-xl font-black text-[#2A1A0A] mb-6">
            Total compra: Bs. {{ totalCarritoCompra.toFixed(2) }}
          </div>

          <div class="mb-6">
            <label class="block text-sm font-bold text-gray-700 mb-1">📝 Notas (factura, referencia, etc.)</label>
            <input v-model="notasCompra" type="text" placeholder="Ej: Factura #001..."
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
          </div>

          <div class="flex gap-4">
            <button @click="registrarCompra" :disabled="loading"
              class="flex-1 bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-lg transition-colors disabled:opacity-50">
              {{ loading ? '⏳ Registrando...' : '✅ Registrar Compra' }}
            </button>
            <button @click="carritoCompra = []"
              class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-lg transition-colors">
              🗑️ Limpiar
            </button>
          </div>
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

// ── FILTROS ───────────────────────────────────────────────────────────
const filtros = ref({ busqueda: '', categoria: '' })

const productosFiltrados = computed(() =>
  productos.value.filter(p => {
    const coincideBusqueda =
      p.nombre.toLowerCase().includes(filtros.value.busqueda.toLowerCase()) ||
      p.codigo.includes(filtros.value.busqueda)
    const coincideCategoria =
      filtros.value.categoria === '' || p.categoria === filtros.value.categoria
    return coincideBusqueda && coincideCategoria
  })
)

const stockCritico = computed(() =>
  productos.value.filter(p => p.stock <= p.stock_minimo)
)

const calcularMargen = (compra, venta) => {
  if (!compra || compra === 0) return 100.0
  return (((venta - compra) / compra) * 100).toFixed(1)
}

const resumenPresentaciones = (p) => {
  if (!p.presentaciones || p.presentaciones.length === 0) return '—'
  return p.presentaciones.map(pr => `${pr.nombre} (${pr.unidades_base})`).join(', ')
}

// ── NUEVO PRODUCTO ────────────────────────────────────────────────────
const formNuevo = ref({
  codigo: '', nombre: '', categoria_id: null, unidad: 'unidad',
  precio_compra: 0, precio_venta: 0, stock: 0, stock_minimo: 5,
  descripcion: '', presentaciones: []
})

const stockHelperNuevo = ref({ presentacionIdx: 0, cantidad: 0, sueltas: 0 })

const agregarPresentacionNuevo = () => {
  formNuevo.value.presentaciones.push({
    nombre: '', unidades_base: 1, precio_venta: 0, precio_compra: 0,
    orden: formNuevo.value.presentaciones.length
  })
}
const quitarPresentacionNuevo = (idx) => {
  formNuevo.value.presentaciones.splice(idx, 1)
  if (stockHelperNuevo.value.presentacionIdx >= formNuevo.value.presentaciones.length) {
    stockHelperNuevo.value.presentacionIdx = 0
  }
}

// Auto-calcular stock total cuando hay presentaciones
watch(
  () => [stockHelperNuevo.value.presentacionIdx, stockHelperNuevo.value.cantidad, stockHelperNuevo.value.sueltas, formNuevo.value.presentaciones],
  () => {
    if (formNuevo.value.presentaciones.length === 0) return
    const pres = formNuevo.value.presentaciones[stockHelperNuevo.value.presentacionIdx]
    const uds = pres ? (pres.unidades_base || 1) : 1
    formNuevo.value.stock = (stockHelperNuevo.value.cantidad || 0) * uds + (stockHelperNuevo.value.sueltas || 0)
  },
  { deep: true }
)

const guardarNuevoProducto = async () => {
  loading.value = true
  try {
    await inventarioService.crearProducto(formNuevo.value)
    alert(`✅ Producto "${formNuevo.value.nombre}" guardado. Stock: ${formNuevo.value.stock} unidades`)
    formNuevo.value = {
      codigo: '', nombre: '', categoria_id: null, unidad: 'unidad',
      precio_compra: 0, precio_venta: 0, stock: 0, stock_minimo: 5,
      descripcion: '', presentaciones: []
    }
    stockHelperNuevo.value = { presentacionIdx: 0, cantidad: 0, sueltas: 0 }
    await cargarDatos()
    activeTab.value = 'lista'
  } catch (e) {
    alert('❌ Error al guardar: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

// ── EDITAR PRODUCTO ───────────────────────────────────────────────────
const productoAEditarId = ref(null)
const formEditar = ref(null)
const busquedaEdicion = ref('')

const productosFiltradosParaEditar = computed(() => {
  const term = busquedaEdicion.value.toLowerCase()
  return productos.value.filter(p =>
    p.nombre.toLowerCase().includes(term) || p.codigo.toLowerCase().includes(term)
  )
})

const cargarDatosEdicion = () => {
  if (!productoAEditarId.value) { formEditar.value = null; return }
  const prod = productos.value.find(p => p.id === productoAEditarId.value)
  if (prod) {
    formEditar.value = {
      ...prod,
      // clonamos para no mutar la lista original antes de guardar
      presentaciones: JSON.parse(JSON.stringify(prod.presentaciones || []))
    }
  }
}

const agregarPresentacionEditar = () => {
  formEditar.value.presentaciones.push({
    nombre: '', unidades_base: 1, precio_venta: 0, precio_compra: 0,
    orden: formEditar.value.presentaciones.length
  })
}
const quitarPresentacionEditar = (idx) => {
  formEditar.value.presentaciones.splice(idx, 1)
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
      stock_minimo: formEditar.value.stock_minimo,
      unidad: formEditar.value.unidad,
      presentaciones: formEditar.value.presentaciones.map(p => ({
        nombre: p.nombre,
        unidades_base: p.unidades_base,
        precio_venta: p.precio_venta,
        precio_compra: p.precio_compra || 0,
        orden: p.orden ?? 0
      }))
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

// ── COMPRAS ───────────────────────────────────────────────────────────
const compraTemp = ref({
  productoId: null,
  presentacionIdx: null,     // null = unidad suelta
  cantidadPresentacion: 0,
  unidadesSueltas: 0,
  cantidad: 0,               // total unidades base
  precio: 0                  // precio compra por unidad base
})
const carritoCompra = ref([])
const notasCompra = ref('')

const productoSeleccionadoCompra = computed(() =>
  productos.value.find(p => p.id === compraTemp.value.productoId) || null
)

const tienePresentacionesCompra = computed(() => {
  const prod = productoSeleccionadoCompra.value
  return !!(prod && prod.presentaciones && prod.presentaciones.length > 0)
})

const presentacionSeleccionadaCompra = computed(() => {
  const prod = productoSeleccionadoCompra.value
  if (!prod || compraTemp.value.presentacionIdx === null) return null
  return prod.presentaciones[compraTemp.value.presentacionIdx] || null
})

// Al cambiar de producto
watch(() => compraTemp.value.productoId, (newId) => {
  const prod = productos.value.find(p => p.id === newId)
  if (prod) {
    compraTemp.value.precio = prod.precio_compra || 0
    compraTemp.value.presentacionIdx = (prod.presentaciones && prod.presentaciones.length > 0) ? 0 : null
    compraTemp.value.cantidadPresentacion = 0
    compraTemp.value.unidadesSueltas = 0
    compraTemp.value.cantidad = compraTemp.value.presentacionIdx === null ? 1 : 0
  } else {
    compraTemp.value = { productoId: null, presentacionIdx: null, cantidadPresentacion: 0, unidadesSueltas: 0, cantidad: 0, precio: 0 }
  }
})

// Al cambiar la presentación seleccionada, sugerir precio por unidad base
watch(() => compraTemp.value.presentacionIdx, (idx) => {
  const prod = productoSeleccionadoCompra.value
  if (!prod) return
  if (idx === null) {
    compraTemp.value.precio = prod.precio_compra || 0
    compraTemp.value.cantidad = 1
  } else {
    const pres = prod.presentaciones[idx]
    if (pres && pres.unidades_base > 0) {
      compraTemp.value.precio = pres.precio_compra > 0
        ? parseFloat((pres.precio_compra / pres.unidades_base).toFixed(4))
        : (prod.precio_compra || 0)
    }
    compraTemp.value.cantidad = 0
  }
  compraTemp.value.cantidadPresentacion = 0
  compraTemp.value.unidadesSueltas = 0
})

// Auto-calcular cantidad total cuando se recibe por presentación
watch(
  () => [compraTemp.value.cantidadPresentacion, compraTemp.value.unidadesSueltas],
  () => {
    if (compraTemp.value.presentacionIdx === null) return
    const pres = presentacionSeleccionadaCompra.value
    const uds = pres ? (pres.unidades_base || 1) : 1
    compraTemp.value.cantidad = (compraTemp.value.cantidadPresentacion || 0) * uds + (compraTemp.value.unidadesSueltas || 0)
  }
)

const agregarAlCarritoCompra = () => {
  if (!compraTemp.value.productoId || compraTemp.value.cantidad <= 0) return
  const prod = productoSeleccionadoCompra.value
  const pres = presentacionSeleccionadaCompra.value

  carritoCompra.value.push({
    productoId: prod.id,
    nombre: prod.nombre,
    presentacion_nombre: pres ? pres.nombre : null,
    presentacion_cantidad: pres ? compraTemp.value.cantidadPresentacion : null,
    cantidad: compraTemp.value.cantidad,
    precio_unitario: compraTemp.value.precio,
    subtotal: compraTemp.value.cantidad * compraTemp.value.precio
  })

  compraTemp.value = { productoId: null, presentacionIdx: null, cantidadPresentacion: 0, unidadesSueltas: 0, cantidad: 0, precio: 0 }
}

const eliminarDelCarritoCompra = (index) => carritoCompra.value.splice(index, 1)

const totalCarritoCompra = computed(() =>
  carritoCompra.value.reduce((acc, item) => acc + item.subtotal, 0)
)

const registrarCompra = async () => {
  loading.value = true
  try {
    const result = await inventarioService.registrarCompra(
      carritoCompra.value, notasCompra.value, proveedorId.value
    )
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