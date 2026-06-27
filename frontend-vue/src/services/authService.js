import api from './api';

const authService = {
  /**
   * Inicia sesión y guarda el token en localStorage
   * @param {string} username 
   * @param {string} password 
   */
  async login(username, password) {
    try {
      const response = await api.post('/auth/login', { username, password });
      
      // Asumimos que el backend devuelve { token: "...", user: { ... } }
      if (response.data.token) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
        localStorage.setItem('token', response.data.token);
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.message || 'Error al iniciar sesión';
    }
  },

  /**
   * Cierra la sesión eliminando los datos del almacenamiento
   */
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login'; // Redirección forzada al login
  },

  /**
   * Obtiene el usuario actual desde el almacenamiento local
   */
  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
  },

  /**
   * Verifica si hay un token válido presente
   */
  isAuthenticated() {
    const token = localStorage.getItem('token');
    return !!token;
  },

  /**
   * Obtiene el token para usarlo en los headers de axios
   */
  getToken() {
    return localStorage.getItem('token');
  }
};

export default authService;