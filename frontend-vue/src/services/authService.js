import api from './api';

const authService = {
  async login(username, password) {
    try {
      // ✅ OAuth2 requiere form-urlencoded, no JSON
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      // ✅ El backend devuelve access_token, no token
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify({
          username: username,
          role: response.data.role  // lo agregaremos en el backend
        }));
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Error al iniciar sesión';
    }
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
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