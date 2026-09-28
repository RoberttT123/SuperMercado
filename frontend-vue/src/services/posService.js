import api from './api';

const posService = {
  async buscarPorCodigo(codigo) {
    const res = await api.get('/inventario/productos/buscar', { params: { codigo } });
    return res.data;
  },

  async buscarPorNombre(nombre) {
    const res = await api.get('/inventario/productos/buscar', { params: { nombre } });
    return res.data;
  },

  async procesarVenta(payload) {
    const res = await api.post('/ventas/', payload);
    return res.data;
  },

  async getResumenHoy() {
    const hoy = new Date().toISOString().split('T')[0];
    const res = await api.get('/reportes/ventas/resumen', {
      params: { inicio: hoy, fin: hoy }
    });
    return res.data;
  },

  async descargarPDF(ventaId) {
    const res = await api.get(`/ventas/${ventaId}/pdf`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Venta_${ventaId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => window.URL.revokeObjectURL(url), 1000);
  }
};

export default posService;