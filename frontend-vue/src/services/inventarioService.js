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
  async getProveedores() {
    const res = await api.get('/proveedores/');
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
  async agregarNivel(productoId, nivel) {
    const res = await api.post(`/inventario/productos/${productoId}/niveles`, nivel);
    return res.data;
  },
  async editarNivel(nivelId, data) {
    const res = await api.put(`/inventario/niveles/${nivelId}`, data);
    return res.data;
  },
  async eliminarNivel(nivelId) {
    const res = await api.delete(`/inventario/niveles/${nivelId}`);
    return res.data;
  },
  async registrarCompra(items, notas, proveedor_id = null) {
    const res = await api.post('/inventario/compras', { items, notas, proveedor_id });
    return res.data;
  }
};

export default inventarioService;