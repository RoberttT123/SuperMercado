import api from './api';

const reportesService = {
  async getStockCriticoReporte() {
    const res = await api.get('/reportes/stock-critico');
    return res.data;
  },
  async getReporteRentabilidad(inicio, fin) {
    const res = await api.get('/reportes/rentabilidad', { params: { inicio, fin } });
    return res.data;
  }
};

export default reportesService;