import { defineStore } from 'pinia';
import authService from '@/services/authService';

export const useAuthStore = defineStore('auth', {
  // Estado: datos persistentes
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
  }),

  // Getters: propiedades computadas
  getters: {
    isAuthenticated: (state) => !!state.token,
    userName: (state) => state.user?.name || 'Usuario',
  },

  // Acciones: métodos para modificar el estado
  actions: {
    async login(username, password) {
      try {
        const data = await authService.login(username, password);
        // authService ya guarda en localStorage, aquí actualizamos el estado reactivo
        this.token = data.token;
        this.user = data.user;
        return { success: true };
      } catch (error) {
        return { success: false, message: error };
      }
    },

    logout() {
      authService.logout(); // Limpia localStorage
      this.token = null;
      this.user = null;
    },

    // Permite refrescar el estado si se recarga la página
    initializeAuth() {
      this.token = localStorage.getItem('token');
      this.user = JSON.parse(localStorage.getItem('user'));
    }
  }
});