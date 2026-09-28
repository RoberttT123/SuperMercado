import api from './api';

const reportesService = {
  async getStockCriticoReporte() {
    const res = await api.get('/reportes/stock-critico');
    return res.data;
  },
  async getReporteRentabilidad(inicio, fin) {
    const res = await api.get('/reportes/rentabilidad', { params: { inicio, fin } });
    return res.data;
  },
  async descargarExcel(inicio, fin) {
    const res = await api.get('/reportes/excel', { params: { inicio, fin }, responseType: 'blob' });
    return res.data;
  },
  async getComprasLista(inicio, fin) {
    const res = await api.get('/reportes/compras/lista', { params: { inicio, fin } });
    return res.data;
  },
  async getComprasResumen(inicio, fin) {
    const res = await api.get('/reportes/compras/resumen', { params: { inicio, fin } });
    return res.data;
  },
  async getDetalleCompra(compraId) {
    const res = await api.get(`/inventario/compras/${compraId}/detalle`);
    return res.data;
  }
};

export default reportesService;