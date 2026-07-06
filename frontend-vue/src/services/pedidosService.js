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

  async getHistorial(vendedor = null) {
    const params = vendedor ? { vendedor } : {};
    const res = await api.get('/pedidos/historial', { params });
    return res.data;
  },

  async crearPedido(data) {
    const res = await api.post('/pedidos/', data);
    return res.data;
  },

  async editarPedido(id, data) {
    const res = await api.put(`/pedidos/${id}/editar`, data);
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

  // ✅ Helper interno para abrir/descargar PDFs
  _abrirPDF(blob, nombreArchivo) {
    const fileURL = window.URL.createObjectURL(
      new Blob([blob], { type: 'application/pdf' })
    )
    // En móvil descarga, en desktop abre en nueva pestaña
    const link = document.createElement('a')
    link.href = fileURL
    link.setAttribute('download', nombreArchivo)
    link.setAttribute('target', '_blank')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    // Liberar memoria
    setTimeout(() => window.URL.revokeObjectURL(fileURL), 1000)
  },

  // PDF Nota de Preventa
  async descargarPDF(pedidoId) {
    try {
      const res = await api.get(`/pedidos/${pedidoId}/pdf`, {
        responseType: 'blob'
      })
      this._abrirPDF(res.data, `preventa_${pedidoId}.pdf`)
    } catch (error) {
      console.error('Error al generar PDF de preventa:', error)
      alert('Hubo un problema al generar el PDF.')
    }
  },

  // PDF Nota de Venta final
  async descargarNotaVenta(pedidoId) {
    try {
      const res = await api.get(`/pedidos/${pedidoId}/nota-venta`, {
        responseType: 'blob'
      })
      this._abrirPDF(res.data, `nota_venta_${pedidoId}.pdf`)
    } catch (error) {
      console.error('Error al generar Nota de Venta:', error)
      alert('Hubo un problema al generar el PDF.')
    }
  }
}

export default pedidosService