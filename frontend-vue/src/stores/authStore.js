import { defineStore } from 'pinia';
import authService from '@/services/authService';
import router from '@/router';  // ← importa el router

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userName: (state) => state.user?.username || 'Usuario',
    userRole: (state) => state.user?.role || null,
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    async login(username, password) {
      try {
        const data = await authService.login(username, password);
        this.token = data.access_token;
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
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      this.token = null;
      this.user = null;
      // ✅ Usa el router directamente
      router.push('/login');
    },

    initializeAuth() {
      this.token = localStorage.getItem('token');
      this.user = JSON.parse(localStorage.getItem('user'));
    }
  }
});