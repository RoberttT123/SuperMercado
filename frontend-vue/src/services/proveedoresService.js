import api from './api';

const proveedoresService = {
  async getProveedores() {
    const res = await api.get('/proveedores/');
    return res.data;
  },
  async getProveedor(id) {
    const res = await api.get(`/proveedores/${id}`);
    return res.data;
  },
  async getComprasProveedor(id) {
    const res = await api.get(`/proveedores/${id}/compras`);
    return res.data;
  },
  async crearProveedor(data) {
    const res = await api.post('/proveedores/', data);
    return res.data;
  },
  async actualizarProveedor(id, data) {
    const res = await api.put(`/proveedores/${id}`, data);
    return res.data;
  },
  async desactivarProveedor(id) {
    const res = await api.delete(`/proveedores/${id}`);
    return res.data;
  }
};

export default proveedoresService;