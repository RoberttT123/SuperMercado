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
  }
};

export default posService;