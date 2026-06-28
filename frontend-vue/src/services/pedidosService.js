import api from './api';

const pedidosService = {
  async getPedidosPendientes(vendedor = null) {
    const params = vendedor ? { vendedor } : {};
    const res = await api.get('/pedidos/pendientes', { params });
    return res.data;
  },
  async getPedido(id) {
    const res = await api.get(`/pedidos/${id}`);
    return res.data;
  },
  async crearPedido(data) {
    const res = await api.post('/pedidos/', data);
    return res.data;
  },
  async getHistorial(vendedor = null) {
  const params = vendedor ? { vendedor } : {};
  const res = await api.get('/pedidos/historial', { params });
  return res.data;
    },
  async cancelarPedido(id) {
    const res = await api.put(`/pedidos/${id}/cancelar`);
    return res.data;
  },
  async entregarPedido(id, data) {
    const res = await api.put(`/pedidos/${id}/entregar`, data);
    return res.data;
  },
  async editarPedido(id, data) {
  const res = await api.put(`/pedidos/${id}/editar`, data);
  return res.data;
    },
  descargarPDF(id) {
    window.open(`http://localhost:8000/pedidos/${id}/pdf`, '_blank');
  }
};

export default pedidosService;