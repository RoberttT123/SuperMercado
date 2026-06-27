import api from './api';

const inventarioService = {
  // ─── Categorías ───────────────────────────────────────────────────────────
  async getCategorias() {
    try {
      const response = await api.get('/categorias');
      return response.data;
    } catch (error) {
      console.error("Error al obtener categorías:", error);
      return [];
    }
  },

  // ─── Productos ────────────────────────────────────────────────────────────
  async getProductos(termino = "", categoriaId = null) {
    try {
      // Si hay filtros, los enviamos como parámetros de consulta
      const params = {};
      if (termino) params.termino = termino;
      if (categoriaId) params.categoria_id = categoriaId;

      const response = await api.get('/productos', { params });
      return response.data;
    } catch (error) {
      console.error("Error al buscar productos:", error);
      return [];
    }
  },

  async getProductoPorCodigo(codigo) {
    try {
      const response = await api.get(`/productos/codigo/${codigo}`);
      return response.data;
    } catch (error) {
      return null;
    }
  },

  async crearProducto(datos) {
    try {
      const response = await api.post('/productos', datos);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Error al crear producto";
    }
  },

  async actualizarProducto(id, datos) {
    try {
      const response = await api.put(`/productos/${id}`, datos);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Error al actualizar producto";
    }
  },

  async desactivarProducto(id) {
    try {
      await api.delete(`/productos/${id}`);
    } catch (error) {
      throw error.response?.data?.detail || "Error al eliminar producto";
    }
  },

  // ─── Stock ────────────────────────────────────────────────────────────────
  async getStockCritico() {
    try {
      const response = await api.get('/stock/critico');
      return response.data;
    } catch (error) {
      return [];
    }
  },

  async ajustarStock(id, cantidad) {
    try {
      await api.post(`/productos/${id}/stock`, { cantidad });
    } catch (error) {
      throw error.response?.data?.detail || "Error al ajustar stock";
    }
  },

  // ─── Compras ──────────────────────────────────────────────────────────────
  /**
   * @param {Array} items - [{producto_id, cantidad, precio_unitario}, ...]
   */
  async registrarCompra(items, proveedorId = null, notas = "") {
    try {
      const response = await api.post('/compras', {
        items,
        proveedor_id: proveedorId,
        notas
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || "Error al registrar compra";
    }
  }
};

export default inventarioService;