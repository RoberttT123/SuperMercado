/**
 * src/services/reportesService.js
 * Servicio para obtener datos de análisis, gráficos y KPIs
 */
import api from './api';

const reportesService = {
  /**
   * Obtiene los KPIs principales para el Dashboard
   * @returns {Promise<Object>} { ventas_hoy, transacciones_hoy, productos_bajos, caja_activa }
   */
  async getDashboardKPIs() {
    try {
      const response = await api.get('/reportes/kpi');
      return response.data;
    } catch (error) {
      console.error("Error al cargar KPIs del dashboard:", error);
      return {
        ventas_hoy: 0,
        transacciones_hoy: 0,
        productos_bajos: 0,
        caja_activa: false
      };
    }
  },

  /**
   * Datos para gráficos de ventas por rango de fechas
   * @param {string} fechaInicio - Formato YYYY-MM-DD
   * @param {string} fechaFin - Formato YYYY-MM-DD
   */
  async getVentasPorPeriodo(fechaInicio, fechaFin) {
    try {
      const response = await api.get('/reportes/ventas-periodo', {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
      });
      return response.data; // Esperado: [{fecha: '2026-06-26', total: 500}, ...]
    } catch (error) {
      return [];
    }
  },

  /**
   * Reporte de productos con inventario crítico
   */
  async getStockCriticoReporte() {
    try {
      const response = await api.get('/reportes/stock-critico');
      return response.data;
    } catch (error) {
      return [];
    }
  },

  /**
   * Reporte consolidado de ganancias (Ventas vs Costos)
   * Útil para ver la rentabilidad real del negocio
   */
  async getReporteRentabilidad(fechaInicio, fechaFin) {
    try {
      const response = await api.get('/reportes/rentabilidad', {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
      });
      return response.data;
    } catch (error) {
      throw new Error("No se pudo generar el reporte de rentabilidad");
    }
  },

  /**
   * Exportación de datos (Ejemplo para Excel/CSV)
   * Si tu backend genera archivos, este servicio descarga el blob
   */
  async descargarReporteExcel(tipo, fechaInicio, fechaFin) {
    try {
      const response = await api.get(`/reportes/exportar/${tipo}`, {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
        responseType: 'blob' 
      });
      
      // Crear un link de descarga temporal
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Reporte_${tipo}_${fechaInicio}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error al descargar archivo:", error);
    }
  }
};

export default reportesService;