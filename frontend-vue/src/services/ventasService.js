/**
 * src/services/ventasService.js
 * Servicio para gestión de Punto de Venta (POS)
 */
import api from './api';

const ventasService = {
  // ─── Procesar Venta ────────────────────────────────────────────────────────

  /**
   * @param {Object} data - { carrito, caja_id, metodo_pago, descuento, monto_recibido, notas }
   */
  async procesarVenta(data) {
    try {
      const response = await api.post('/ventas/procesar', {
        carrito: data.carrito, // [{producto_id, cantidad, precio_unitario, precio_compra}]
        caja_id: data.caja_id,
        metodo_pago: data.metodo_pago || 'efectivo',
        descuento: data.descuento || 0,
        monto_recibido: data.monto_recibido || 0,
        notas: data.notas || ''
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Error al procesar la venta";
    }
  },

  // ─── Anulación ─────────────────────────────────────────────────────────────

  async anularVenta(ventaId) {
    try {
      const response = await api.post(`/ventas/anular/${ventaId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Error al anular la venta";
    }
  },

  // ─── Consultas de Ventas ───────────────────────────────────────────────────

  async getVentasDelDia() {
    try {
      const response = await api.get('/ventas/hoy');
      return response.data;
    } catch (error) {
      console.error("Error al obtener ventas del día:", error);
      return [];
    }
  },

  async getDetalleVenta(ventaId) {
    try {
      const response = await api.get(`/ventas/detalle/${ventaId}`);
      return response.data;
    } catch (error) {
      console.error("Error al obtener detalle:", error);
      return [];
    }
  },

  async getVentasPorRango(fechaInicio, fechaFin) {
    try {
      const response = await api.get('/ventas/rango', {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
      });
      return response.data;
    } catch (error) {
      console.error("Error en rango de fechas:", error);
      return [];
    }
  },

  // ─── Métricas y Reportes ───────────────────────────────────────────────────

  async getResumenVentas(fechaInicio, fechaFin) {
    try {
      const response = await api.get('/ventas/resumen', {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
      });
      return response.data;
    } catch (error) {
      return {
        total_transacciones: 0,
        ingresos_totales: 0,
        descuentos: 0,
        ticket_promedio: 0,
        efectivo: 0,
        qr: 0,
        tarjeta: 0
      };
    }
  },

  async getProductosMasVendidos(fechaInicio, fechaFin, limite = 10) {
    try {
      const response = await api.get('/ventas/mas-vendidos', {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin, limite }
      });
      return response.data;
    } catch (error) {
      console.error("Error en reporte de productos:", error);
      return [];
    }
  },

  // ─── Utilidades del Carrito (Frontend Logic) ───────────────────────────────
  
  /**
   * Calcula totales de un carrito en el frontend para evitar llamadas innecesarias al server
   */
  calcularTotales(carrito, descuento = 0) {
    const subtotal = carrito.reduce((acc, item) => acc + (item.cantidad * item.precio_unitario), 0);
    const total = Math.max(0, subtotal - descuento);
    return { subtotal, total };
  }
};

export default ventasService;