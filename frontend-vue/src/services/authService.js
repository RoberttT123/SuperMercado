import api from './api';

const authService = {
  async login(username, password) {
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify({
          username: response.data.username,
          role: response.data.role
        }));
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Error al iniciar sesión';
    }
  },

  // ✅ Solo limpia storage — la navegación la maneja el store
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
  },

  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  getToken() {
    return localStorage.getItem('token');
  }
};

export default authService;