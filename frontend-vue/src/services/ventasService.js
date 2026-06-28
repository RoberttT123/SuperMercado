import api from './api';

const ventasService = {
  async getResumenVentas(inicio, fin) {
    const res = await api.get('/reportes/ventas/resumen', { params: { inicio, fin } });
    return res.data;
  },
  async getVentasPorRango(inicio, fin) {
    const res = await api.get('/reportes/ventas/lista', { params: { inicio, fin } });
    return res.data;
  },
  async getProductosMasVendidos(inicio, fin) {
    const res = await api.get('/reportes/ventas/top-productos', { params: { inicio, fin } });
    return res.data;
  },
  async getDetalleVenta(ventaId) {
    const res = await api.get(`/ventas/${ventaId}/detalle`);
    return res.data;
  }
};

export default ventasService;