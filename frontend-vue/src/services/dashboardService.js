import api from './api';

const dashboardService = {
  async getResumen() {
    const res = await api.get('/dashboard/resumen');
    return res.data; // ahora incluye top_productos adentro
  },
  async getVentasSemana() {
    const res = await api.get('/dashboard/ventas-semana');
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
  // getTopProductos() eliminado
};

export default dashboardService;