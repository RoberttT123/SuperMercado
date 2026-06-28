import api from './api';

const cajaService = {
  async getCajaActiva() {
    const res = await api.get('/caja/activa');
    return res.data;
  },
  async abrirCaja(monto, usuario) {
    const res = await api.post('/caja/abrir', { monto_inicial: monto, usuario });
    return res.data;
  },
  async cerrarCaja(cajaId, montoContado, notas) {
    const res = await api.post(`/caja/cerrar/${cajaId}`, {
      monto_contado: montoContado,
      notas
    });
    return res.data;
  },
  async getResumenCaja(cajaId) {
    const res = await api.get(`/caja/${cajaId}/resumen`);
    return res.data;
  },
  async getHistorial() {
    const res = await api.get('/caja/historial');
    return res.data;
  }
};

export default cajaService;