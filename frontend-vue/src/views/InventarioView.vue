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
                <th class="pb-2 text-center">Unidad</th>
                <th class="pb-2 text-center">Uds/Caja</th>
                <th class="pb-2 text-right">Compra/Ud</th>
                <th class="pb-2 text-right">Venta/Ud</th>
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
                <td class="py-3 text-center text-sm text-gray-500">{{ p.unidad }}</td>
                <td class="py-3 text-center text-sm text-gray-400">
                  <span v-if="p.unidad === 'caja' || p.unidad === 'paquete'">{{ p.unidades_por_caja || 1 }}</span>
                  <span v-else class="text-gray-300">—</span>
                </td>
                <td class="py-3 text-right text-sm">Bs. {{ p.precio_compra.toFixed(2) }}</td>
                <td class="py-3 text-right font-bold">Bs. {{ p.precio_venta.toFixed(2) }}</td>
                <td class="py-3 text-right text-sm text-gray-500">{{ calcularMargen(p.precio_compra, p.precio_venta) }}%</td>
                <td class="py-3 text-center font-bold" :class="p.stock <= p.stock_minimo ? 'text-red-600' : ''">{{ p.stock }}</td>
                <td class="py-3 text-center text-sm text-gray-400">{{ p.stock_minimo }}</td>
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
                <label class="block text-sm font-bold text-gray-700 mb-1">📐 Tipo de unidad</label>
                <select v-model="formNuevo.unidad"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  <option value="unidad">unidad</option>
                  <option value="kg">kg</option>
                  <option value="litro">litro</option>
                  <option value="bolsa">bolsa</option>
                  <option value="caja">caja ← tiene unidades internas</option>
                  <option value="paquete">paquete ← tiene unidades internas</option>
                </select>
              </div>
            </div>

            <!-- Columna derecha -->
            <div class="space-y-4">

              <!-- ✅ Solo si es CAJA o PAQUETE: configuración de caja -->
              <div v-if="formNuevo.unidad === 'caja' || formNuevo.unidad === 'paquete'"
                class="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-3">
                <div class="text-xs font-black text-blue-700 uppercase tracking-wide">
                  📦 Configuración de {{ formNuevo.unidad }}
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Unidades por {{ formNuevo.unidad }}</label>
                    <input v-model.number="formNuevo.unidades_por_caja" type="number" min="1" step="1"
                      class="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:border-blue-500 bg-white text-center font-bold text-lg">
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Precio por {{ formNuevo.unidad }} (Bs.)</label>
                    <input v-model.number="formNuevo._precio_caja" type="number" step="0.5" min="0"
                      class="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:border-blue-500 bg-white">
                  </div>
                </div>

                <div class="bg-white rounded-lg p-2 border border-blue-100 flex justify-between items-center">
                  <span class="text-xs text-gray-500">Precio compra por unidad (auto)</span>
                  <span class="font-black text-blue-700">Bs. {{ formNuevo.precio_compra.toFixed(4) }}</span>
                </div>

                <!-- Stock con cajas -->
                <div class="border-t border-blue-200 pt-3">
                  <div class="text-xs font-black text-blue-700 uppercase mb-2">Stock inicial</div>
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label class="block text-xs font-bold text-gray-600 mb-1">{{ formNuevo.unidad === 'caja' ? 'Cajas' : 'Paquetes' }}</label>
                      <input v-model.number="formNuevo._cajas_stock" type="number" min="0" step="1"
                        class="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:border-blue-500 bg-white text-center font-bold">
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-gray-600 mb-1">Unidades sueltas</label>
                      <input v-model.number="formNuevo._unidades_sueltas" type="number" min="0" step="1"
                        class="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:border-blue-500 bg-white text-center">
                    </div>
                  </div>
                  <div class="mt-2 bg-white rounded-lg p-2 border border-blue-100 flex justify-between items-center">
                    <span class="text-xs text-gray-500">
                      Total: {{ formNuevo._cajas_stock || 0 }} × {{ formNuevo.unidades_por_caja || 1 }} + {{ formNuevo._unidades_sueltas || 0 }}
                    </span>
                    <span class="font-black text-blue-700">{{ formNuevo.stock }} unidades</span>
                  </div>
                </div>
              </div>

              <!-- ✅ Para unidades simples (unidad, kg, litro, bolsa) -->
              <div v-else>
                <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
                  <div class="text-xs font-bold text-gray-500 uppercase mb-3">💰 Precios</div>
                  <div class="space-y-3">
                    <div>
                      <label class="block text-xs font-bold text-gray-600 mb-1">Precio de compra (Bs.)</label>
                      <input v-model.number="formNuevo.precio_compra" type="number" step="0.1" min="0"
                        class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4 mt-4">
                  <div>
                    <label class="block text-sm font-bold text-gray-700 mb-1">📦 Stock inicial</label>
                    <input v-model.number="formNuevo.stock" type="number" step="1" min="0"
                      class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  </div>
                  <div>
                    <label class="block text-sm font-bold text-gray-700 mb-1">⚠️ Stock mínimo</label>
                    <input v-model.number="formNuevo.stock_minimo" type="number" step="1" min="0"
                      class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
                  </div>
                </div>
              </div>

              <!-- Stock mínimo para caja/paquete -->
              <div v-if="formNuevo.unidad === 'caja' || formNuevo.unidad === 'paquete'">
                <label class="block text-sm font-bold text-gray-700 mb-1">⚠️ Stock mínimo (unidades)</label>
                <input v-model.number="formNuevo.stock_minimo" type="number" step="1" min="0"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>

              <!-- Precio de venta (siempre) -->
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">💰 Precio de venta por unidad (Bs.) *</label>
                <input v-model.number="formNuevo.precio_venta" type="number" step="0.1" min="0" required
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📄 Descripción (opcional)</label>
            <textarea v-model="formNuevo.descripcion" rows="2"
              class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]"></textarea>
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
                <label class="block text-sm font-bold text-gray-700 mb-1">
                  📦 Stock actual
                  <span v-if="formEditar.unidad === 'caja' || formEditar.unidad === 'paquete'" class="text-xs font-normal text-gray-400">(en unidades)</span>
                </label>
                <input v-model.number="formEditar.stock" type="number" step="1" min="0"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">⚠️ Stock mínimo (unidades)</label>
                <input v-model.number="formEditar.stock_minimo" type="number" step="1" min="0"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>

              <!-- Tipo de unidad (readonly para edición) -->
              <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                <div class="text-xs text-gray-400 mb-1">Tipo de unidad</div>
                <div class="font-bold text-gray-700 capitalize">{{ formEditar.unidad }}</div>
              </div>
            </div>

            <!-- Columna derecha -->
            <div class="space-y-4">

              <!-- Solo si es caja/paquete -->
              <div v-if="formEditar.unidad === 'caja' || formEditar.unidad === 'paquete'"
                class="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-3">
                <div class="text-xs font-black text-blue-700 uppercase tracking-wide">
                  📦 Configuración de {{ formEditar.unidad }}
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Unidades por {{ formEditar.unidad }}</label>
                    <input v-model.number="formEditar.unidades_por_caja" type="number" min="1" step="1"
                      class="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:border-blue-500 bg-white text-center font-bold text-lg">
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Precio por {{ formEditar.unidad }} (Bs.)</label>
                    <input v-model.number="formEditar._precio_caja" type="number" step="0.5" min="0"
                      class="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:border-blue-500 bg-white">
                  </div>
                </div>

                <div class="bg-white rounded-lg p-2 border border-blue-100 flex justify-between items-center">
                  <span class="text-xs text-gray-500">Precio compra por unidad (auto)</span>
                  <span class="font-black text-blue-700">
                    Bs. {{ formEditar.precio_compra ? formEditar.precio_compra.toFixed(4) : '0.0000' }}
                  </span>
                </div>
              </div>

              <!-- Para unidades simples -->
              <div v-else>
                <label class="block text-sm font-bold text-gray-700 mb-1">💸 Precio de compra (Bs.)</label>
                <input v-model.number="formEditar.precio_compra" type="number" step="0.1" min="0"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
              </div>

              <!-- Precio venta siempre -->
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">💰 Precio venta por unidad (Bs.)</label>
                <input v-model.number="formEditar.precio_venta" type="number" step="0.1" min="0"
                  class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B]">
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
              {{ p.codigo }} — {{ p.nombre }} ({{ p.unidad }})
            </option>
          </select>
        </div>

        <!-- Panel de entrada según tipo de producto -->
        <div v-if="compraTemp.productoId" class="mb-6">

          <!-- ✅ CAJA O PAQUETE -->
          <div v-if="esCajaOPaquete" class="bg-blue-50 border border-blue-200 rounded-xl p-5 space-y-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-lg">📦</span>
              <div>
                <div class="font-black text-blue-800">{{ productoSeleccionadoCompra.nombre }}</div>
                <div class="text-xs text-blue-600">
                  {{ productoSeleccionadoCompra.unidades_por_caja || 1 }} unidades por {{ productoSeleccionadoCompra.unidad }}
                </div>
              </div>
            </div>

            <!-- Inputs cajas + sueltas -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">
                  N° de {{ productoSeleccionadoCompra.unidad === 'caja' ? 'cajas' : 'paquetes' }}
                </label>
                <input v-model.number="compraTemp.cajas" type="number" min="0" step="1"
                  class="w-full px-4 py-3 rounded-xl border-2 border-blue-300 focus:outline-none focus:border-blue-500 bg-white text-center font-black text-xl">
              </div>
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Unidades sueltas (opcional)</label>
                <input v-model.number="compraTemp.unidades_sueltas" type="number" min="0" step="1"
                  class="w-full px-4 py-3 rounded-xl border-2 border-blue-200 focus:outline-none focus:border-blue-400 bg-white text-center font-bold text-xl">
              </div>
            </div>

            <!-- Cálculo total -->
            <div class="bg-white rounded-xl p-3 border border-blue-200">
              <div class="flex justify-between items-center text-sm mb-1">
                <span class="text-gray-500">
                  {{ compraTemp.cajas || 0 }} × {{ productoSeleccionadoCompra.unidades_por_caja || 1 }} + {{ compraTemp.unidades_sueltas || 0 }} sueltas
                </span>
                <span class="font-black text-blue-700 text-lg">= {{ compraTemp.cantidad }} unidades</span>
              </div>
            </div>

            <!-- Precios -->
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-white rounded-xl p-3 border border-blue-100">
                <div class="text-xs text-gray-400 uppercase mb-1">
                  Precio compra/{{ productoSeleccionadoCompra.unidad }}
                </div>
                <div class="font-black text-blue-700 text-lg">
                  Bs. {{ precioCajaActual.toFixed(2) }}
                </div>
                <div class="text-xs text-gray-400">
                  (Bs. {{ (productoSeleccionadoCompra.precio_compra || 0).toFixed(2) }} × {{ productoSeleccionadoCompra.unidades_por_caja || 1 }} u.)
                </div>
              </div>
              <div class="bg-white rounded-xl p-3 border border-orange-100">
                <div class="text-xs text-gray-400 uppercase mb-1">Precio venta/unidad</div>
                <div class="font-black text-[#FF6B2B] text-lg">
                  Bs. {{ (productoSeleccionadoCompra.precio_venta || 0).toFixed(2) }}
                </div>
                <div class="text-xs text-green-600">
                  Margen: {{ calcularMargen(productoSeleccionadoCompra.precio_compra, productoSeleccionadoCompra.precio_venta) }}%
                </div>
              </div>
            </div>

            <!-- Precio compra por unidad (editable) -->
            <div>
              <label class="block text-xs font-bold text-gray-600 mb-1">
                Precio compra por unidad (Bs.) — editable si cambió
              </label>
              <input v-model.number="compraTemp.precio" type="number" step="0.01" min="0"
                class="w-full px-3 py-2 rounded-lg border border-blue-200 focus:outline-none focus:border-blue-500 bg-white">
            </div>

            <!-- Subtotal -->
            <div class="bg-blue-700 text-white rounded-xl p-3 flex justify-between items-center">
              <span class="font-bold">Subtotal de esta entrada</span>
              <span class="font-black text-xl">Bs. {{ (compraTemp.cantidad * compraTemp.precio).toFixed(2) }}</span>
            </div>

            <button @click="agregarAlCarrito" :disabled="!compraTemp.cantidad || compraTemp.cantidad <= 0"
              class="w-full bg-gray-800 hover:bg-black text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50">
              ➕ Agregar {{ compraTemp.cantidad }} unidades al carrito
            </button>
          </div>

          <!-- ✅ UNIDAD SIMPLE (unidad, kg, litro, bolsa) -->
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
                <input v-model.number="compraTemp.precio" type="number" step="0.5" min="0"
                  class="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:outline-none focus:border-[#FF6B2B] bg-white">
              </div>
            </div>

            <!-- Precios del producto -->
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-white rounded-xl p-3 border border-gray-100">
                <div class="text-xs text-gray-400 uppercase mb-1">Precio compra registrado</div>
                <div class="font-black text-gray-700">
                  Bs. {{ (productoSeleccionadoCompra.precio_compra || 0).toFixed(2) }}
                </div>
              </div>
              <div class="bg-white rounded-xl p-3 border border-orange-100">
                <div class="text-xs text-gray-400 uppercase mb-1">Precio venta actual</div>
                <div class="font-black text-[#FF6B2B]">
                  Bs. {{ (productoSeleccionadoCompra.precio_venta || 0).toFixed(2) }}
                </div>
              </div>
            </div>

            <!-- Subtotal -->
            <div class="bg-gray-700 text-white rounded-xl p-3 flex justify-between items-center">
              <span class="font-bold">Subtotal</span>
              <span class="font-black text-xl">Bs. {{ (compraTemp.cantidad * compraTemp.precio).toFixed(2) }}</span>
            </div>

            <button @click="agregarAlCarrito" :disabled="!compraTemp.productoId"
              class="w-full bg-gray-800 hover:bg-black text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50">
              ➕ Agregar al carrito
            </button>
          </div>
        </div>

        <!-- Placeholder si no hay producto seleccionado -->
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
                <div class="text-xs text-gray-400">{{ item.cantidad }} unid. × Bs. {{ item.precio_unitario.toFixed(2) }}</div>
              </div>
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

const esCajaOPaqueteUnidad = (unidad) =>
  unidad === 'caja' || unidad === 'paquete'

// ── NUEVO PRODUCTO ────────────────────────────────────────────────────
const formNuevo = ref({
  codigo: '', nombre: '', categoria_id: null, unidad: 'unidad',
  precio_compra: 0, precio_venta: 0, stock: 0, stock_minimo: 5,
  descripcion: '', unidades_por_caja: 1,
  _precio_caja: 0,      // helper UI
  _cajas_stock: 0,      // helper UI
  _unidades_sueltas: 0  // helper UI
})

// Reset campos de caja cuando cambia unidad a tipo simple
watch(() => formNuevo.value.unidad, (unidad) => {
  if (!esCajaOPaqueteUnidad(unidad)) {
    formNuevo.value.unidades_por_caja = 1
    formNuevo.value._precio_caja = 0
    formNuevo.value._cajas_stock = 0
    formNuevo.value._unidades_sueltas = 0
  }
})

// Auto-calcular precio_compra (solo para caja/paquete)
watch(
  () => [formNuevo.value._precio_caja, formNuevo.value.unidades_por_caja, formNuevo.value.unidad],
  ([precioCaja, uds, unidad]) => {
    if (esCajaOPaqueteUnidad(unidad) && precioCaja > 0 && uds > 0) {
      formNuevo.value.precio_compra = parseFloat((precioCaja / uds).toFixed(4))
    }
  }
)

// Auto-calcular stock total (solo para caja/paquete)
watch(
  () => [formNuevo.value._cajas_stock, formNuevo.value._unidades_sueltas, formNuevo.value.unidades_por_caja, formNuevo.value.unidad],
  ([cajas, sueltas, uds, unidad]) => {
    if (esCajaOPaqueteUnidad(unidad)) {
      formNuevo.value.stock = (cajas || 0) * (uds || 1) + (sueltas || 0)
    }
  }
)

const guardarNuevoProducto = async () => {
  loading.value = true
  try {
    const { _precio_caja, _cajas_stock, _unidades_sueltas, ...datos } = formNuevo.value
    await inventarioService.crearProducto(datos)
    alert(`✅ Producto "${formNuevo.value.nombre}" guardado. Stock: ${formNuevo.value.stock} unidades`)
    formNuevo.value = {
      codigo: '', nombre: '', categoria_id: null, unidad: 'unidad',
      precio_compra: 0, precio_venta: 0, stock: 0, stock_minimo: 5,
      descripcion: '', unidades_por_caja: 1,
      _precio_caja: 0, _cajas_stock: 0, _unidades_sueltas: 0
    }
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
      _precio_caja: esCajaOPaqueteUnidad(prod.unidad)
        ? parseFloat((prod.precio_compra * (prod.unidades_por_caja || 1)).toFixed(2))
        : 0
    }
  }
}

watch(
  () => formEditar.value ? [formEditar.value._precio_caja, formEditar.value.unidades_por_caja, formEditar.value.unidad] : null,
  (vals) => {
    if (!vals || !formEditar.value) return
    const [precioCaja, uds, unidad] = vals
    if (esCajaOPaqueteUnidad(unidad) && precioCaja > 0 && uds > 0) {
      formEditar.value.precio_compra = parseFloat((precioCaja / uds).toFixed(4))
    }
  },
  { deep: true }
)

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
      unidades_por_caja: formEditar.value.unidades_por_caja
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
  cantidad: 0,          // total unidades (calculado)
  precio: 0,            // precio por unidad
  cajas: 0,             // para caja/paquete
  unidades_sueltas: 0   // para caja/paquete
})
const carritoCompra = ref([])
const notasCompra = ref('')

const productoSeleccionadoCompra = computed(() =>
  productos.value.find(p => p.id === compraTemp.value.productoId) || null
)

const esCajaOPaquete = computed(() => {
  const prod = productoSeleccionadoCompra.value
  return prod && esCajaOPaqueteUnidad(prod.unidad)
})

// Precio de caja calculado del producto seleccionado
const precioCajaActual = computed(() => {
  const prod = productoSeleccionadoCompra.value
  if (!prod) return 0
  return (prod.precio_compra || 0) * (prod.unidades_por_caja || 1)
})

// Cuando cambia el producto
watch(() => compraTemp.value.productoId, (newId) => {
  if (newId) {
    const prod = productos.value.find(p => p.id === newId)
    if (prod) {
      compraTemp.value.precio = prod.precio_compra
      compraTemp.value.cajas = 0
      compraTemp.value.unidades_sueltas = 0
      // Para simple: cantidad 1, para caja: 0 hasta que ingrese cajas
      compraTemp.value.cantidad = esCajaOPaqueteUnidad(prod.unidad) ? 0 : 1
    }
  } else {
    compraTemp.value.precio = 0
    compraTemp.value.cajas = 0
    compraTemp.value.unidades_sueltas = 0
    compraTemp.value.cantidad = 0
  }
})

// Auto-calcular cantidad total para caja/paquete
watch(
  () => [compraTemp.value.cajas, compraTemp.value.unidades_sueltas],
  ([cajas, sueltas]) => {
    const prod = productoSeleccionadoCompra.value
    if (prod && esCajaOPaquete.value) {
      const uds = prod.unidades_por_caja || 1
      compraTemp.value.cantidad = (cajas || 0) * uds + (sueltas || 0)
    }
  }
)

const agregarAlCarrito = () => {
  if (!compraTemp.value.productoId || compraTemp.value.cantidad <= 0) return
  const prod = productoSeleccionadoCompra.value

  carritoCompra.value.push({
    productoId: prod.id,
    nombre: prod.nombre,
    cantidad: compraTemp.value.cantidad,
    precio_unitario: compraTemp.value.precio,
    subtotal: compraTemp.value.cantidad * compraTemp.value.precio
  })

  // Reset
  compraTemp.value = {
    productoId: null, cantidad: 0,
    precio: 0, cajas: 0, unidades_sueltas: 0
  }
}

const eliminarDelCarrito = (index) => carritoCompra.value.splice(index, 1)

const totalCarrito = computed(() =>
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