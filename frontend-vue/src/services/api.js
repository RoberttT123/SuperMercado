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

// Mientras se usa el sistema, el backend renueva la sesión y manda el token
// nuevo en esta cabecera; guardarlo evita que la sesión venza a mitad de turno.
const guardarTokenRenovado = (response) => {
  const nuevo = response?.headers?.['x-nuevo-token'];
  if (nuevo) localStorage.setItem('token', nuevo);
};

api.interceptors.response.use(
  (response) => {
    guardarTokenRenovado(response);
    return response;
  },
  (error) => {
    guardarTokenRenovado(error.response);
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // ✅ Usa router — funciona con hash y history mode
      if (router.currentRoute.value.name !== 'login') {
        // El login muestra este aviso para que la persona sepa por qué volvió ahí
        const detalle = error.response.data?.detail;
        sessionStorage.setItem('avisoLogin', typeof detalle === 'string' ? detalle : 'Tu sesión expiró, vuelve a iniciar sesión');
        router.push('/login');
      }
    }
    return Promise.reject(error);
  }
);

export default api;