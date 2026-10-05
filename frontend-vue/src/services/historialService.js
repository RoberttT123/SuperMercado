import api from './api';

// Módulo Historial de movimientos — el backend solo responde al admin.
const historialService = {
  async listar(params) {
    const res = await api.get('/historial/movimientos', { params });
    return res.data;
  },
  async getUsuarios() {
    const res = await api.get('/historial/usuarios');
    return res.data;
  },
  async descargarExcel(params) {
    const res = await api.get('/historial/excel', { params, responseType: 'blob', timeout: 60000 });
    return res.data;
  }
};

export default historialService;
