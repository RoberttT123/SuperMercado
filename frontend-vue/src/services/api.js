import axios from 'axios';
import router from '@/router';  // ← importa el router

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Accept': 'application/json' },
  timeout: 15000
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json';
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // ✅ Usa router — funciona con hash y history mode
      if (router.currentRoute.value.name !== 'login') {
        router.push('/login');
      }
    }
    return Promise.reject(error);
  }
);

export default api;