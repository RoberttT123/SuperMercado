/**
 * src/services/api.js
 * Configuración centralizada de Axios para todas las peticiones HTTP.
 */
import axios from 'axios';

// Configuración base de la API
const api = axios.create({
  baseURL: 'http://localhost:8000', // Asegúrate de que coincida con tu backend
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 15000 // Timeout de 15 segundos
});

/**
 * Interceptor de Petición (Request)
 * Se ejecuta antes de cada llamada: inyecta el token de autenticación automáticamente
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Interceptor de Respuesta (Response)
 * Se ejecuta después de cada respuesta: maneja errores globales como sesiones expiradas
 */
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Si el servidor responde con 401 (No autorizado), significa que el token expiró o es inválido
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Redirigir al login si el usuario no está ya allí
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    // Rechazar la promesa para que el servicio específico que llamó a la API pueda manejar el error
    return Promise.reject(error);
  }
);

export default api;