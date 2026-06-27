import api from './api';

const inventarioService = {
  async getProductos() {
    const res = await api.get('/inventario/productos');
    return res.data;
  },
  async getCategorias() {
    const res = await api.get('/inventario/categorias');
    return res.data;
  },
  async crearProducto(data) {
    const res = await api.post('/inventario/productos', data);
    return res.data;
  },
  async actualizarProducto(id, data) {
    const res = await api.put(`/inventario/productos/${id}`, data);
    return res.data;
  },
  async registrarCompra(items, notas) {
    const res = await api.post('/inventario/compras', { items, notas });
    return res.data;
  }
};

export default inventarioService;