import api from './api';

const cajaService = {
  /**
   * Obtiene la caja actualmente abierta
   */
  async getCajaAbierta() {
    try {
      const response = await api.get('/caja/activa');
      return response.data; // Retorna el objeto caja o null
    } catch (error) {
      console.error("Error al obtener caja abierta:", error);
      return null;
    }
  },

  /**
   * Abre una nueva caja
   * @param {number} montoInicial 
   * @param {string} usuario 
   */
  async abrirCaja(montoInicial, usuario = "Admin") {
    try {
      const response = await api.post('/caja/abrir', { 
        monto_inicial: montoInicial, 
        usuario 
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Error al abrir caja";
    }
  },

  /**
   * Cierra la caja actual
   * @param {number} cajaId 
   * @param {number} montoFinal 
   * @param {string} notas 
   */
  async cerrarCaja(cajaId, montoFinal, notas = "") {
    try {
      const response = await api.post(`/caja/cerrar/${cajaId}`, { 
        monto_final: montoFinal, 
        notas 
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Error al cerrar caja";
    }
  },

  /**
   * Obtiene resumen de ventas de la caja actual para el arqueo
   * @param {number} cajaId 
   */
  async getResumenCaja(cajaId) {
    try {
      const response = await api.get(`/caja/resumen/${cajaId}`);
      return response.data;
    } catch (error) {
      console.error("Error al obtener resumen:", error);
      return { total_transacciones: 0, total_ingresos: 0, efectivo: 0, qr: 0, tarjeta: 0 };
    }
  },

  /**
   * Historial de cajas cerradas
   */
  async getHistorialCajas(limite = 30) {
    try {
      const response = await api.get(`/caja/historial?limite=${limite}`);
      return response.data;
    } catch (error) {
      console.error("Error al obtener historial:", error);
      return [];
    }
  }
};

export default cajaService;