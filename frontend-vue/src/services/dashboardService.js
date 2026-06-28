import api from './api';

const dashboardService = {
  async getResumen() {
    const res = await api.get('/dashboard/resumen');
    return res.data;
  },
  async getVentasSemana() {
    const res = await api.get('/dashboard/ventas-semana');
    return res.data;
  },
  async getTopProductos() {
    const res = await api.get('/dashboard/top-productos');
    return res.data;
  },
  async getUltimasVentas() {
    const res = await api.get('/dashboard/ultimas-ventas');
    return res.data;
  },
  async getStockCritico() {
    const res = await api.get('/dashboard/stock-critico');
    return res.data;
  }
};

export default dashboardService;