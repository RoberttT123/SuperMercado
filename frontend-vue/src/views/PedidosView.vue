<template>
  <div class="p-6 max-w-full">
    <div class="mb-6 border-b border-[#FFE0CC] pb-4">
      <h1 class="text-3xl font-black text-[#FF6B2B] mb-1">📋 Pedidos</h1>
      <p class="text-gray-500 text-sm">Toma pedidos en visita y conviértelos en ventas al entregar.</p>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 mb-6 overflow-x-auto">
      <button @click="activeTab = 'nuevo'"
        :class="['whitespace-nowrap px-6 py-3 font-bold text-sm transition-colors',
          activeTab === 'nuevo' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        📝 Nuevo Pedido
      </button>
      <button @click="activeTab = 'pendientes'; cargarPendientes()"
        :class="['whitespace-nowrap px-6 py-3 font-bold text-sm transition-colors relative',
          activeTab === 'pendientes' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        📦 Pendientes
        <span v-if="pedidosPendientes.length > 0"
          class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-black w-5 h-5 rounded-full flex items-center justify-center">
          {{ pedidosPendientes.length }}
        </span>
      </button>
      <button @click="activeTab = 'historial'; cargarHistorial()"
        :class="['whitespace-nowrap px-6 py-3 font-bold text-sm transition-colors',
          activeTab === 'historial' ? 'text-[#FF6B2B] border-b-2 border-[#FF6B2B]' : 'text-gray-500 hover:text-gray-700']">
        📊 Mi Historial
      </button>
    </div>

    <div class="bg-white rounded-2xl p-6 border border-[#FFE0CC] shadow-sm">

      <!-- ══════════════════════════════════════════════
           TAB 1 — NUEVO PEDIDO
      ══════════════════════════════════════════════ -->
      <div v-if="activeTab === 'nuevo'">
        <h2 class="text-lg font-bold text-[#FF6B2B] mb-6">Tomar pedido en visita</h2>

        <!-- Datos del cliente -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">👤 Nombre del cliente *</label>
            <input v-model="formPedido.cliente" type="text" placeholder="Ej: Don Solomeo Paredes"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-base">
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">📝 Notas (opcional)</label>
            <input v-model="formPedido.notas" type="text" placeholder="Ej: entregar el martes"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-base">
          </div>
        </div>

        <!-- Búsqueda de productos -->
        <div class="mb-4">
          <label class="block text-sm font-bold text-gray-700 mb-1">🔍 Buscar producto</label>
          <input v-model="busquedaProducto" type="text" placeholder="Escribe el nombre del producto..."
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-base">
        </div>

        <!-- Resultados búsqueda -->
        <div v-if="busquedaProducto && productosBuscados.length > 0"
          class="mb-6 border border-gray-200 rounded-xl overflow-hidden">
          <div v-for="prod in productosBuscados" :key="prod.id"
            class="flex items-center justify-between p-4 border-b border-gray-100 last:border-0 hover:bg-orange-50 transition-colors">
            <div>
              <div class="font-bold text-sm">{{ prod.nombre }}</div>
              <div class="text-xs text-gray-400">{{ prod.codigo }} · Bs. {{ prod.precio_venta.toFixed(2) }}</div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-xs font-bold"
                :class="prod.stock > 5 ? 'text-green-600' : prod.stock > 0 ? 'text-yellow-600' : 'text-red-500'">
                Stock: {{ prod.stock }}
              </span>
              <input type="number" min="1" :max="prod.stock || 999" v-model.number="cantidadesTemp[prod.id]"
                class="w-16 px-2 py-1 border rounded-lg text-center text-sm focus:outline-none focus:border-[#FF6B2B]">
              <button @click="agregarAlPedido(prod)"
                class="bg-[#FF6B2B] text-white text-sm font-bold px-4 py-2 rounded-xl hover:bg-[#E85510] transition-colors">
                ➕
              </button>
            </div>
          </div>
        </div>

        <div v-else-if="busquedaProducto"
          class="mb-6 p-3 bg-gray-50 rounded-lg text-sm text-gray-400 border border-gray-200">
          No se encontraron productos con "{{ busquedaProducto }}"
        </div>

        <!-- Items del pedido -->
        <div v-if="itemsPedido.length > 0" class="mb-6">
          <h3 class="font-bold text-gray-700 mb-3">📋 Productos del pedido ({{ itemsPedido.length }})</h3>
          <div class="border border-gray-200 rounded-xl overflow-hidden mb-4">
            <div v-for="(item, index) in itemsPedido" :key="index"
              class="flex items-center justify-between p-3 border-b border-gray-100 last:border-0 hover:bg-gray-50">
              <div class="flex-1">
                <div class="font-bold text-sm">{{ item.nombre }}</div>
                <div class="text-xs text-gray-400">Bs. {{ item.precio_venta.toFixed(2) }} c/u</div>
              </div>
              <div class="flex items-center gap-4">
                <input type="number" min="1" v-model.number="item.cantidad"
                  class="w-16 px-2 py-1 border rounded-lg text-center text-sm focus:outline-none focus:border-[#FF6B2B]">
                <span class="text-sm font-bold w-24 text-right">
                  Bs. {{ (item.precio_venta * item.cantidad).toFixed(2) }}
                </span>
                <button @click="itemsPedido.splice(index, 1)"
                  class="text-red-500 hover:text-red-700 font-bold px-2">🗑️</button>
              </div>
            </div>
          </div>

          <!-- Total del pedido -->
          <div class="text-right font-black text-lg text-[#2A1A0A] mb-4">
            Total estimado: Bs. {{ itemsPedido.reduce((a, i) => a + i.precio_venta * i.cantidad, 0).toFixed(2) }}
          </div>

          <div class="flex gap-4">
            <button @click="guardarPedido" :disabled="guardando || !formPedido.cliente"
              class="flex-1 bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50 text-base">
              {{ guardando ? '⏳ Guardando...' : '💾 Guardar Pedido' }}
            </button>
            <button @click="limpiarPedido"
              class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-xl transition-colors">
              🗑️ Limpiar
            </button>
          </div>
        </div>

        <div v-else class="text-center py-10 text-gray-400 bg-gray-50 rounded-xl border border-gray-200">
          <div class="text-4xl mb-2">📦</div>
          <div class="font-bold">Busca productos arriba para agregar al pedido</div>
        </div>

        <!-- Banner último pedido guardado -->
        <div v-if="ultimoPedidoGuardado"
          class="mt-4 p-4 bg-green-50 border border-green-200 rounded-xl">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="font-bold text-green-800">✅ Pedido {{ ultimoPedidoGuardado.numero }} guardado</div>
              <div class="text-sm text-green-700">Cliente: {{ ultimoPedidoGuardado.cliente }}</div>
            </div>
          </div>
          <!-- ✅ Dos botones PDF -->
          <div class="flex gap-3">
            <button @click="pedidosService.descargarPDF(ultimoPedidoGuardado.id)"
              class="flex-1 bg-white border border-green-300 text-green-700 font-bold text-sm px-4 py-2 rounded-xl hover:bg-green-100 transition-colors">
              📋 Nota de Preventa
            </button>
            <button @click="ultimoPedidoGuardado = null"
              class="bg-gray-100 hover:bg-gray-200 text-gray-500 font-bold text-sm px-4 py-2 rounded-xl transition-colors">
              ✕ Cerrar
            </button>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════
           TAB 2 — PEDIDOS PENDIENTES
      ══════════════════════════════════════════════ -->
      <div v-if="activeTab === 'pendientes'">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#FF6B2B]">Pedidos Pendientes de Entrega</h2>
          <button @click="cargarPendientes"
            class="text-sm bg-gray-100 hover:bg-gray-200 font-bold px-4 py-2 rounded-lg transition-colors">
            🔄 Actualizar
          </button>
        </div>

        <!-- Banner última entrega -->
        <div v-if="ultimaEntrega"
          class="mb-4 p-4 bg-green-50 border border-green-200 rounded-xl">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="font-bold text-green-800">🎉 Entrega confirmada</div>
              <div class="text-sm text-green-700">
                {{ ultimaEntrega.cliente }} · Venta {{ ultimaEntrega.numero_venta }} · Bs. {{ ultimaEntrega.total.toFixed(2) }}
              </div>
            </div>
          </div>
          <!-- ✅ Dos botones PDF -->
          <div class="flex gap-3">
            <button @click="pedidosService.descargarPDF(ultimaEntrega.pedido_id)"
              class="flex-1 bg-white border border-green-200 text-green-700 font-bold text-sm px-3 py-2 rounded-xl hover:bg-green-50 transition-colors">
              📋 Preventa
            </button>
            <button @click="pedidosService.descargarNotaVenta(ultimaEntrega.pedido_id)"
              class="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold text-sm px-3 py-2 rounded-xl transition-colors">
              🧾 Nota de Venta
            </button>
            <button @click="ultimaEntrega = null"
              class="bg-gray-100 hover:bg-gray-200 text-gray-500 font-bold text-sm px-3 py-2 rounded-xl transition-colors">
              ✕
            </button>
          </div>
        </div>

        <div v-if="cargando" class="text-center py-8 text-gray-400">⏳ Cargando...</div>

        <div v-else-if="pedidosPendientes.length === 0"
          class="text-center py-10 text-gray-400 bg-gray-50 rounded-xl border border-gray-200">
          <div class="text-4xl mb-2">🎉</div>
          <div class="font-bold">No hay pedidos pendientes</div>
        </div>

        <div v-else class="space-y-4">
          <div v-for="pedido in pedidosPendientes" :key="pedido.id"
            class="border border-gray-200 rounded-xl overflow-hidden">

            <!-- Header del pedido -->
            <div class="flex items-center justify-between p-4 bg-gray-50 cursor-pointer"
              @click="togglePedido(pedido.id)">
              <div>
                <div class="font-black text-[#FF6B2B]">{{ pedido.numero }}</div>
                <div class="text-sm font-bold text-gray-700">{{ pedido.cliente }}</div>
                <div class="text-xs text-gray-400">
                  {{ formatoFecha(pedido.fecha) }}
                  <span v-if="pedido.notas"> · 📝 {{ pedido.notas }}</span>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span class="bg-yellow-100 text-yellow-700 text-xs font-bold px-3 py-1 rounded-full">
                  ⏳ Pendiente
                </span>
                <span class="text-gray-400">{{ pedidoAbierto === pedido.id ? '▲' : '▼' }}</span>
              </div>
            </div>

            <!-- Detalle expandible -->
            <div v-if="pedidoAbierto === pedido.id" class="p-4 border-t border-gray-100">
              <div v-if="!detallesPedidos[pedido.id]" class="text-center py-4 text-gray-400">
                ⏳ Cargando...
              </div>
              <div v-else>

                <!-- ── MODO EDICIÓN ────────────────────────── -->
                <div v-if="editandoId === pedido.id">
                  <div class="bg-blue-50 border border-blue-200 rounded-xl p-3 mb-4">
                    <div class="font-bold text-blue-800 text-sm mb-1">✏️ Modo edición</div>
                    <div class="text-xs text-blue-600">Edita cantidades, elimina o agrega productos. Guarda cuando termines.</div>
                  </div>

                  <!-- Notas editables -->
                  <div class="mb-4">
                    <label class="block text-xs font-bold text-gray-600 mb-1">📝 Notas del pedido</label>
                    <input v-model="formEdicionPedido.notas" type="text"
                      placeholder="Ej: entregar el martes..."
                      class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-sm">
                  </div>

                  <!-- Items editables -->
                  <div class="mb-4">
                    <div class="text-xs font-bold text-gray-500 uppercase mb-2">Productos del pedido</div>
                    <div class="space-y-2">
                      <div v-for="(item, index) in formEdicionPedido.items" :key="index"
                        class="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-xl">
                        <div class="flex-1">
                          <div class="font-bold text-sm">{{ item.nombre }}</div>
                          <div class="text-xs text-gray-400">Bs. {{ item.precio_venta.toFixed(2) }} c/u</div>
                        </div>
                        <div class="flex items-center gap-2">
                          <button @click="item.cantidad = Math.max(1, item.cantidad - 1)"
                            class="w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-lg font-black text-gray-600 flex items-center justify-center transition-colors">
                            −
                          </button>
                          <input type="number" min="1" v-model.number="item.cantidad"
                            class="w-14 text-center border border-gray-200 rounded-lg py-1 text-sm font-bold focus:outline-none focus:border-[#FF6B2B]">
                          <button @click="item.cantidad++"
                            class="w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-lg font-black text-gray-600 flex items-center justify-center transition-colors">
                            +
                          </button>
                        </div>
                        <span class="text-sm font-bold w-20 text-right">
                          Bs. {{ (item.precio_venta * item.cantidad).toFixed(2) }}
                        </span>
                        <button @click="formEdicionPedido.items.splice(index, 1)"
                          class="text-red-500 hover:text-red-700 w-8 h-8 flex items-center justify-center bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Agregar producto -->
                  <div class="mb-4 bg-gray-50 p-3 rounded-xl border border-gray-200">
                    <div class="text-xs font-bold text-gray-600 uppercase mb-2">➕ Agregar producto</div>
                    <input v-model="busquedaEdicion" type="text"
                      placeholder="Buscar producto para agregar..."
                      class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-sm mb-2">
                    <div v-if="productosParaEdicion.length > 0"
                      class="border border-gray-200 rounded-lg overflow-hidden">
                      <div v-for="prod in productosParaEdicion" :key="prod.id"
                        class="flex items-center justify-between p-2 hover:bg-orange-50 border-b border-gray-100 last:border-0 cursor-pointer transition-colors"
                        @click="agregarProductoEdicion(prod)">
                        <div>
                          <div class="font-bold text-xs">{{ prod.nombre }}</div>
                          <div class="text-[10px] text-gray-400">Bs. {{ prod.precio_venta.toFixed(2) }} · Stock: {{ prod.stock }}</div>
                        </div>
                        <span class="text-[#FF6B2B] font-black text-lg">+</span>
                      </div>
                    </div>
                  </div>

                  <!-- Total edición -->
                  <div class="text-right font-black text-base text-[#2A1A0A] mb-4">
                    Total estimado: Bs. {{ totalEdicion.toFixed(2) }}
                  </div>

                  <!-- Botones guardar/cancelar -->
                  <div class="flex gap-3">
                    <button @click="guardarEdicionPedido(pedido.id)"
                      :disabled="guardandoEdicion || formEdicionPedido.items.length === 0"
                      class="flex-1 bg-[#FF6B2B] hover:bg-[#E85510] text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50">
                      {{ guardandoEdicion ? '⏳ Guardando...' : '💾 Guardar cambios' }}
                    </button>
                    <button @click="cancelarEdicion"
                      class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-xl transition-colors">
                      Cancelar
                    </button>
                  </div>
                </div>

                <!-- ── MODO VISTA NORMAL ───────────────────── -->
                <div v-else>
                  <!-- Tabla items -->
                  <table class="w-full text-left border-collapse mb-4">
                    <thead>
                      <tr class="border-b border-gray-100 text-xs text-gray-500">
                        <th class="pb-2">Producto</th>
                        <th class="pb-2 text-center">Cant.</th>
                        <th class="pb-2 text-right">P. Venta</th>
                        <th class="pb-2 text-right">Subtotal</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="item in detallesPedidos[pedido.id]" :key="item.id"
                        class="border-b border-gray-50">
                        <td class="py-2 text-sm font-medium">{{ (item.productos || {}).nombre || '—' }}</td>
                        <td class="py-2 text-sm text-center font-bold">{{ item.cantidad }}</td>
                        <td class="py-2 text-sm text-right">Bs. {{ item.precio_venta.toFixed(2) }}</td>
                        <td class="py-2 text-sm text-right font-bold">
                          Bs. {{ (item.cantidad * item.precio_venta).toFixed(2) }}
                        </td>
                      </tr>
                    </tbody>
                  </table>

                  <div class="text-right font-black text-lg text-[#2A1A0A] mb-4">
                    Total: Bs. {{ totalPedido(detallesPedidos[pedido.id]).toFixed(2) }}
                  </div>

                  <!-- Panel de entrega -->
                  <div v-if="entregandoId === pedido.id"
                    class="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-4">
                    <h4 class="font-bold text-gray-700 mb-3">💳 Confirmar entrega y cobro</h4>
                    <div class="grid grid-cols-2 gap-4">
                      <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">Método de pago</label>
                        <select v-model="formEntrega.metodo_pago"
                          class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-sm">
                          <option value="efectivo">💵 Efectivo</option>
                          <option value="qr">📱 QR / Transferencia</option>
                          <option value="tarjeta">💳 Tarjeta</option>
                        </select>
                      </div>
                      <div v-if="formEntrega.metodo_pago === 'efectivo'">
                        <label class="block text-xs font-bold text-gray-600 mb-1">Monto recibido</label>
                        <input type="number" v-model.number="formEntrega.monto_recibido" min="0" step="0.5"
                          class="w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-[#FF6B2B] text-sm">
                        <p class="text-xs text-gray-400 mt-1">
                          Cambio: Bs. {{ Math.max(0, formEntrega.monto_recibido - totalPedido(detallesPedidos[pedido.id])).toFixed(2) }}
                        </p>
                      </div>
                    </div>
                    <div class="flex gap-3 mt-4">
                      <button @click="confirmarEntrega(pedido)" :disabled="procesando"
                        class="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50">
                        {{ procesando ? '⏳ Procesando...' : '✅ Confirmar Entrega' }}
                      </button>
                      <button @click="entregandoId = null"
                        class="bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-2 px-4 rounded-xl transition-colors">
                        Cancelar
                      </button>
                    </div>
                  </div>

                  <!-- Botones de acción normales -->
                  <div v-else class="grid grid-cols-2 gap-3">
                    <button @click="iniciarEntrega(pedido)"
                      class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition-colors text-sm">
                      🚚 Marcar Entregado
                    </button>
                    <button @click="iniciarEdicion(pedido)"
                      class="bg-blue-50 text-blue-600 hover:bg-blue-100 font-bold py-3 rounded-xl transition-colors text-sm border border-blue-200">
                      ✏️ Editar Pedido
                    </button>
                    <button @click="pedidosService.descargarPDF(pedido.id)"
                      class="bg-gray-50 text-gray-600 hover:bg-gray-100 font-bold py-2 rounded-xl transition-colors text-sm border border-gray-200">
                      📋 Nota Preventa
                    </button>
                    <button @click="cancelarPedido(pedido)"
                      class="bg-red-50 text-red-500 hover:bg-red-100 font-bold py-2 rounded-xl transition-colors text-sm border border-red-200">
                      ❌ Cancelar pedido
                    </button>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════
           TAB 3 — HISTORIAL
      ══════════════════════════════════════════════ -->
      <div v-if="activeTab === 'historial'">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#FF6B2B]">📊 Mi Historial</h2>
          <button @click="cargarHistorial"
            class="text-sm bg-gray-100 hover:bg-gray-200 font-bold px-4 py-2 rounded-lg transition-colors">
            🔄 Actualizar
          </button>
        </div>

        <!-- KPIs -->
        <div class="grid grid-cols-3 gap-4 mb-6">
          <div class="bg-[#FFF9F6] rounded-2xl p-4 border border-[#FFE0CC] text-center">
            <div class="text-xs text-gray-400 uppercase font-bold mb-1">Total pedidos</div>
            <div class="text-3xl font-black text-[#FF6B2B]">{{ historial.length }}</div>
          </div>
          <div class="bg-[#FFF9F6] rounded-2xl p-4 border border-[#FFE0CC] text-center">
            <div class="text-xs text-gray-400 uppercase font-bold mb-1">Entregados</div>
            <div class="text-3xl font-black text-green-600">
              {{ historial.filter(p => p.estado === 'entregado').length }}
            </div>
          </div>
          <div class="bg-[#FFF9F6] rounded-2xl p-4 border border-[#FFE0CC] text-center">
            <div class="text-xs text-gray-400 uppercase font-bold mb-1">Facturado</div>
            <div class="text-2xl font-black text-[#FF6B2B]">
              Bs. {{ totalFacturado.toFixed(0) }}
            </div>
          </div>
        </div>

        <!-- Filtros -->
        <div class="flex gap-2 mb-4 flex-wrap">
          <button v-for="f in filtrosEstado" :key="f.value"
            @click="filtroActivo = f.value"
            :class="['px-4 py-1.5 rounded-full text-xs font-bold transition-colors border',
              filtroActivo === f.value
                ? 'bg-[#FF6B2B] text-white border-[#FF6B2B]'
                : 'bg-white text-gray-600 border-gray-200 hover:border-[#FF6B2B]']">
            {{ f.label }} ({{ historial.filter(p => f.value === 'todos' || p.estado === f.value).length }})
          </button>
        </div>

        <div v-if="cargandoHistorial" class="text-center py-8 text-gray-400">⏳ Cargando historial...</div>

        <div v-else-if="historialFiltrado.length === 0"
          class="text-center py-10 text-gray-400 bg-gray-50 rounded-xl border border-gray-200">
          <div class="text-4xl mb-2">📭</div>
          <div class="font-bold">No hay pedidos en esta categoría</div>
        </div>

        <div v-else class="space-y-3">
          <div v-for="pedido in historialFiltrado" :key="pedido.id"
            class="border rounded-2xl overflow-hidden"
            :class="{
              'border-green-200 bg-green-50/30': pedido.estado === 'entregado',
              'border-red-200 bg-red-50/30': pedido.estado === 'cancelado',
              'border-yellow-200 bg-yellow-50/30': pedido.estado === 'pendiente'
            }">

            <!-- Header -->
            <div class="flex items-center justify-between p-4 cursor-pointer"
              @click="toggleHistorial(pedido.id)">
              <div class="flex items-center gap-3">
                <div class="text-2xl">
                  {{ pedido.estado === 'entregado' ? '✅' : pedido.estado === 'cancelado' ? '❌' : '⏳' }}
                </div>
                <div>
                  <div class="font-black text-[#FF6B2B] text-sm">{{ pedido.numero }}</div>
                  <div class="font-bold text-gray-800">{{ pedido.cliente }}</div>
                  <div class="text-xs text-gray-400">{{ formatoFecha(pedido.fecha) }}</div>
                </div>
              </div>
              <div class="text-right">
                <div v-if="pedido.estado === 'entregado' && pedido.ventas"
                  class="font-black text-green-600">
                  Bs. {{ pedido.ventas.total.toFixed(2) }}
                </div>
                <div class="text-xs mt-1">
                  <span :class="{
                    'bg-green-100 text-green-700': pedido.estado === 'entregado',
                    'bg-red-100 text-red-600': pedido.estado === 'cancelado',
                    'bg-yellow-100 text-yellow-700': pedido.estado === 'pendiente'
                  }" class="px-2 py-0.5 rounded-full font-bold capitalize">
                    {{ pedido.estado }}
                  </span>
                </div>
                <div class="text-gray-400 text-xs mt-1">
                  {{ historialAbierto === pedido.id ? '▲' : '▼' }}
                </div>
              </div>
            </div>

            <!-- Detalle expandible -->
            <div v-if="historialAbierto === pedido.id"
              class="px-4 pb-4 border-t border-gray-100 pt-4">

              <!-- Info venta generada -->
              <div v-if="pedido.estado === 'entregado' && pedido.ventas"
                class="bg-green-50 border border-green-200 rounded-xl p-3 mb-4 flex justify-between items-center">
                <div>
                  <div class="text-xs text-green-600 font-bold uppercase mb-1">Venta generada</div>
                  <div class="font-black text-green-800">{{ pedido.ventas.numero_venta }}</div>
                  <div class="text-xs text-green-600 capitalize">{{ pedido.ventas.metodo_pago }}</div>
                </div>
                <div class="text-right">
                  <div class="text-xl font-black text-green-700">
                    Bs. {{ pedido.ventas.total.toFixed(2) }}
                  </div>
                  <div class="text-xs text-green-500">
                    {{ formatoFecha(pedido.ventas.fecha) }}
                  </div>
                </div>
              </div>

              <!-- Notas -->
              <div v-if="pedido.notas" class="text-sm text-gray-500 mb-3 italic">
                📝 {{ pedido.notas }}
              </div>

              <!-- Detalle items -->
              <div v-if="!detallesHistorial[pedido.id]" class="text-center py-3">
                <button @click="cargarDetalleHistorial(pedido.id)"
                  class="text-sm text-[#FF6B2B] font-bold hover:underline">
                  Ver productos del pedido →
                </button>
              </div>
              <div v-else>
                <div class="text-xs font-bold text-gray-500 uppercase mb-2">Productos</div>
                <div class="space-y-1 mb-4">
                  <div v-for="item in detallesHistorial[pedido.id]" :key="item.id"
                    class="flex justify-between text-sm py-1.5 border-b border-gray-100 last:border-0">
                    <span class="font-medium">{{ (item.productos || {}).nombre || '—' }}</span>
                    <span class="text-gray-600">
                      x{{ item.cantidad }} · Bs. {{ (item.cantidad * item.precio_venta).toFixed(2) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- ✅ Botones PDF según estado -->
              <div class="flex gap-3 mt-4">
                <!-- Siempre: preventa -->
                <button @click="pedidosService.descargarPDF(pedido.id)"
                  class="flex-1 bg-white border border-[#FFE0CC] text-[#FF6B2B] font-bold py-2 rounded-xl hover:bg-orange-50 transition-colors text-sm">
                  📋 Nota Preventa
                </button>

                <!-- Solo si entregado: nota de venta final -->
                <button
                  v-if="pedido.estado === 'entregado' && pedido.venta_id"
                  @click="pedidosService.descargarNotaVenta(pedido.id)"
                  class="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-2 rounded-xl transition-colors text-sm">
                  🧾 Nota de Venta
                </button>
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
import { useAuthStore } from '@/stores/authStore'
import pedidosService from '@/services/pedidosService'
import inventarioService from '@/services/inventarioService'

const authStore = useAuthStore()
const activeTab = ref('nuevo')
const cargando = ref(false)
const guardando = ref(false)
const procesando = ref(false)
const cargandoHistorial = ref(false)

// ── NUEVO PEDIDO ─────────────────────────────────────────────────────
const formPedido = ref({ cliente: '', notas: '' })
const busquedaProducto = ref('')
const itemsPedido = ref([])
const cantidadesTemp = ref({})
const ultimoPedidoGuardado = ref(null)
const todosProductos = ref([])

onMounted(async () => {
  try {
    todosProductos.value = await inventarioService.getProductos()
  } catch (e) { console.error(e) }
  await cargarPendientes()
})

const productosBuscados = computed(() => {
  if (!busquedaProducto.value) return []
  const term = busquedaProducto.value.toLowerCase()
  return todosProductos.value
    .filter(p => p.nombre.toLowerCase().includes(term) || p.codigo.includes(term))
    .slice(0, 5)
})

const agregarAlPedido = (prod) => {
  const cantidad = cantidadesTemp.value[prod.id] || 1
  const index = itemsPedido.value.findIndex(i => i.producto_id === prod.id)
  if (index !== -1) {
    itemsPedido.value[index].cantidad += cantidad
  } else {
    itemsPedido.value.push({
      producto_id: prod.id,
      nombre: prod.nombre,
      precio_venta: prod.precio_venta,
      precio_compra: prod.precio_compra,
      cantidad
    })
  }
  cantidadesTemp.value[prod.id] = 1
  busquedaProducto.value = ''
}

const guardarPedido = async () => {
  if (!formPedido.value.cliente) {
    alert('⚠️ Ingresa el nombre del cliente')
    return
  }
  guardando.value = true
  try {
    const resultado = await pedidosService.crearPedido({
      cliente: formPedido.value.cliente,
      vendedor: authStore.user?.username,
      notas: formPedido.value.notas,
      items: itemsPedido.value.map(i => ({
        producto_id: i.producto_id,
        cantidad: i.cantidad,
        precio_venta: i.precio_venta
      }))
    })

    ultimoPedidoGuardado.value = {
      numero: resultado.numero,
      cliente: formPedido.value.cliente,
      id: resultado.pedido_id
    }
    limpiarPedido()

    // ✅ Ofrecer descarga de preventa automáticamente
    const descargar = confirm(
      `✅ Pedido ${resultado.numero} guardado\n\n¿Descargar la Nota de Preventa para el cliente?`
    )
    if (descargar) {
      pedidosService.descargarPDF(resultado.pedido_id)
    }
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error al guardar'))
  } finally {
    guardando.value = false
  }
}

const limpiarPedido = () => {
  itemsPedido.value = []
  formPedido.value = { cliente: '', notas: '' }
  busquedaProducto.value = ''
}

// ── PEDIDOS PENDIENTES ───────────────────────────────────────────────
const pedidosPendientes = ref([])
const pedidoAbierto = ref(null)
const detallesPedidos = ref({})
const entregandoId = ref(null)
const formEntrega = ref({ metodo_pago: 'efectivo', monto_recibido: 0 })

// ✅ Guarda el resultado de la última entrega para PDF
const ultimaEntrega = ref(null)

const cargarPendientes = async () => {
  cargando.value = true
  try {
    pedidosPendientes.value = await pedidosService.getPedidosPendientes(
      authStore.user?.username
    )
  } catch (e) { console.error(e) }
  finally { cargando.value = false }
}

const togglePedido = async (id) => {
  if (pedidoAbierto.value === id) { pedidoAbierto.value = null; return }
  pedidoAbierto.value = id
  if (!detallesPedidos.value[id]) {
    try {
      const pedido = await pedidosService.getPedido(id)
      detallesPedidos.value[id] = pedido.items
    } catch (e) { console.error(e) }
  }
}

const totalPedido = (items) => {
  if (!items) return 0
  return items.reduce((acc, i) => acc + i.cantidad * i.precio_venta, 0)
}

const iniciarEntrega = (pedido) => {
  entregandoId.value = pedido.id
  editandoId.value = null
  formEntrega.value = {
    metodo_pago: 'efectivo',
    monto_recibido: totalPedido(detallesPedidos.value[pedido.id])
  }
}

const confirmarEntrega = async (pedido) => {
  procesando.value = true
  try {
    const items = detallesPedidos.value[pedido.id].map(i => ({
      producto_id: i.producto_id,
      cantidad: i.cantidad,
      precio_venta: i.precio_venta,
      precio_compra: 0,
      subtotal: i.cantidad * i.precio_venta
    }))

    const resultado = await pedidosService.entregarPedido(pedido.id, {
      items,
      metodo_pago: formEntrega.value.metodo_pago,
      monto_recibido: formEntrega.value.monto_recibido
    })

    // ✅ Guardar para mostrar botón de descarga
    ultimaEntrega.value = {
      pedido_id: pedido.id,
      numero_pedido: pedido.numero,
      cliente: pedido.cliente,
      numero_venta: resultado.numero_venta,
      total: resultado.total
    }

    entregandoId.value = null
    pedidoAbierto.value = null
    await cargarPendientes()

    // ✅ Ofrecer descarga de nota de venta automáticamente
    const descargar = confirm(
      `✅ Entrega confirmada\n` +
      `Venta: ${resultado.numero_venta}\n` +
      `Total: Bs. ${resultado.total.toFixed(2)}\n\n` +
      `¿Descargar la Nota de Venta para el cliente?`
    )
    if (descargar) {
      pedidosService.descargarNotaVenta(pedido.id)
    }
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error'))
  } finally { procesando.value = false }
}

const cancelarPedido = async (pedido) => {
  if (!confirm(`¿Cancelar pedido ${pedido.numero} de ${pedido.cliente}?`)) return
  try {
    await pedidosService.cancelarPedido(pedido.id)
    await cargarPendientes()
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error'))
  }
}

// ── EDICIÓN DE PEDIDO ────────────────────────────────────────────────
const editandoId = ref(null)
const guardandoEdicion = ref(false)
const busquedaEdicion = ref('')
const formEdicionPedido = ref({ notas: '', items: [] })

const productosParaEdicion = computed(() => {
  if (!busquedaEdicion.value) return []
  const term = busquedaEdicion.value.toLowerCase()
  return todosProductos.value
    .filter(p => p.nombre.toLowerCase().includes(term) || p.codigo.includes(term))
    .slice(0, 5)
})

const totalEdicion = computed(() =>
  formEdicionPedido.value.items.reduce(
    (acc, i) => acc + i.precio_venta * i.cantidad, 0
  )
)

const iniciarEdicion = (pedido) => {
  editandoId.value = pedido.id
  entregandoId.value = null
  busquedaEdicion.value = ''
  const items = detallesPedidos.value[pedido.id] || []
  formEdicionPedido.value = {
    notas: pedido.notas || '',
    items: items.map(i => ({
      producto_id: i.producto_id,
      nombre: (i.productos || {}).nombre || '—',
      precio_venta: i.precio_venta,
      cantidad: i.cantidad
    }))
  }
}

const cancelarEdicion = () => {
  editandoId.value = null
  busquedaEdicion.value = ''
  formEdicionPedido.value = { notas: '', items: [] }
}

const agregarProductoEdicion = (prod) => {
  const existe = formEdicionPedido.value.items.findIndex(i => i.producto_id === prod.id)
  if (existe !== -1) {
    formEdicionPedido.value.items[existe].cantidad++
  } else {
    formEdicionPedido.value.items.push({
      producto_id: prod.id,
      nombre: prod.nombre,
      precio_venta: prod.precio_venta,
      cantidad: 1
    })
  }
  busquedaEdicion.value = ''
}

const guardarEdicionPedido = async (pedidoId) => {
  if (formEdicionPedido.value.items.length === 0) {
    alert('⚠️ El pedido debe tener al menos un producto')
    return
  }
  guardandoEdicion.value = true
  try {
    await pedidosService.editarPedido(pedidoId, {
      notas: formEdicionPedido.value.notas,
      items: formEdicionPedido.value.items.map(i => ({
        producto_id: i.producto_id,
        cantidad: i.cantidad,
        precio_venta: i.precio_venta
      }))
    })
    const pedidoActualizado = await pedidosService.getPedido(pedidoId)
    detallesPedidos.value[pedidoId] = pedidoActualizado.items
    const idx = pedidosPendientes.value.findIndex(p => p.id === pedidoId)
    if (idx !== -1) pedidosPendientes.value[idx].notas = formEdicionPedido.value.notas
    cancelarEdicion()
    alert('✅ Pedido actualizado correctamente')
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'Error al guardar'))
  } finally {
    guardandoEdicion.value = false
  }
}

// ── HISTORIAL ────────────────────────────────────────────────────────
const historial = ref([])
const historialAbierto = ref(null)
const detallesHistorial = ref({})
const filtroActivo = ref('todos')

const filtrosEstado = [
  { value: 'todos',     label: '📋 Todos' },
  { value: 'entregado', label: '✅ Entregados' },
  { value: 'pendiente', label: '⏳ Pendientes' },
  { value: 'cancelado', label: '❌ Cancelados' }
]

const historialFiltrado = computed(() => {
  if (filtroActivo.value === 'todos') return historial.value
  return historial.value.filter(p => p.estado === filtroActivo.value)
})

const totalFacturado = computed(() =>
  historial.value
    .filter(p => p.estado === 'entregado' && p.ventas)
    .reduce((acc, p) => acc + p.ventas.total, 0)
)

const cargarHistorial = async () => {
  cargandoHistorial.value = true
  try {
    historial.value = await pedidosService.getHistorial(authStore.user?.username)
  } catch (e) { console.error(e) }
  finally { cargandoHistorial.value = false }
}

const toggleHistorial = (id) => {
  historialAbierto.value = historialAbierto.value === id ? null : id
}

const cargarDetalleHistorial = async (id) => {
  try {
    const pedido = await pedidosService.getPedido(id)
    detallesHistorial.value[id] = pedido.items
  } catch (e) { console.error(e) }
}

// ── UTILIDADES ───────────────────────────────────────────────────────
const formatoFecha = (f) => {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-BO', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>