import { defineStore } from 'pinia';
import authService from '@/services/authService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    // ✅ el objeto user tiene "username", no "name"
    userName: (state) => state.user?.username || 'Usuario',
    // ✅ getter extra útil para controlar vistas por rol
    userRole: (state) => state.user?.role || null,
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    async login(username, password) {
      try {
        const data = await authService.login(username, password);
        // ✅ el backend devuelve access_token, no token
        this.token = data.access_token;
        // ✅ el backend devuelve username y role, no user
        this.user = {
          username: data.username,
          role: data.role
        };
        return { success: true };
      } catch (error) {
        return { success: false, message: error };
      }
    },

    logout() {
      authService.logout();
      this.token = null;
      this.user = null;
    },

    initializeAuth() {
      this.token = localStorage.getItem('token');
      this.user = JSON.parse(localStorage.getItem('user'));
    }
  }
});