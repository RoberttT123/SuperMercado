import api from './api';

const clientesService = {
  async getClientes(soloConDeuda = false) {
    const res = await api.get('/clientes/', { params: soloConDeuda ? { solo_con_deuda: true } : {} });
    return res.data;
  },
  async buscarCliente(nombre) {
    const res = await api.get('/clientes/buscar', { params: { nombre } });
    return res.data;
  },
  async crearCliente(data) {
    const res = await api.post('/clientes/', data);
    return res.data;
  },
  async actualizarCliente(id, data) {
    const res = await api.put(`/clientes/${id}`, data);
    return res.data;
  },
  async desactivarCliente(id) {
    const res = await api.delete(`/clientes/${id}`);
    return res.data;
  },
  async getMovimientos(id) {
    const res = await api.get(`/clientes/${id}/movimientos`);
    return res.data;
  },
  async registrarAbono(id, monto, motivo) {
    const res = await api.post(`/clientes/${id}/abono`, { monto, motivo });
    return res.data;
  }
};

export default clientesService;