import { defineStore } from 'pinia';
import cajaService from '@/services/cajaService';
import posService from '@/services/posService';

export const useCajaStore = defineStore('caja', {
  state: () => ({
    cajaActiva: null,
    ventasTotalesHoy: 0,
    cargando: false,
  }),

  getters: {
    cajaAbierta: (state) => !!state.cajaActiva,
    montoInicial: (state) => state.cajaActiva?.monto_inicial || 0,
    cajero: (state) => state.cajaActiva?.usuario || '',
    cajaId: (state) => state.cajaActiva?.id || null,
  },

  actions: {
    async cargarEstado() {
      this.cargando = true;
      try {
        this.cajaActiva = await cajaService.getCajaActiva();
        const resumen = await posService.getResumenHoy();
        this.ventasTotalesHoy = resumen.ingresos_totales || 0;
      } catch (e) {
        console.error('Error cargando caja:', e);
      } finally {
        this.cargando = false;
      }
    },

    async abrir(monto, usuario) {
      const caja = await cajaService.abrirCaja(monto, usuario);
      this.cajaActiva = caja; // ✅ Sidebar se actualiza automáticamente
      return caja;
    },

    async cerrar(montoContado, notas) {
      if (!this.cajaId) throw new Error('No hay caja activa');
      const resultado = await cajaService.cerrarCaja(
        this.cajaId, montoContado, notas
      );
      this.cajaActiva = null; // ✅ Sidebar se actualiza automáticamente
      return resultado;
    },

    actualizarVentasHoy(monto) {
      this.ventasTotalesHoy += monto; // ✅ POS actualiza sidebar en tiempo real
    }
  }
});