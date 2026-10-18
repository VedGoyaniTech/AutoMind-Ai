import axios from 'axios';

const resolveApiBase = (): string => {
  // If explicitly provided via VITE_API_URL and not an internal docker hostname
  const viteApiUrl = import.meta.env.VITE_API_URL;
  if (viteApiUrl && !viteApiUrl.includes('://backend')) {
    return `${viteApiUrl.replace(/\/$/, '')}/api/v1`;
  }

  // If VITE_BACKEND_URL is set and not an internal docker hostname (like backend:8000)
  const viteBackendUrl = import.meta.env.VITE_BACKEND_URL;
  if (viteBackendUrl && !viteBackendUrl.includes('://backend')) {
    return `${viteBackendUrl.replace(/\/$/, '')}/api/v1`;
  }

  // In browser environments, use relative path so Vite dev server proxy or reverse proxy handles it seamlessly
  return '/api/v1';
};

const apiBase = resolveApiBase();

const api = axios.create({
  baseURL: apiBase,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('automind_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    // Auto-failover retry: If relative /api/v1 failed with network error on localhost/127.0.0.1, retry directly via http://localhost:8000/api/v1
    if (
      (error.code === 'ERR_NETWORK' || !error.response) &&
      config &&
      !config._retryDirect &&
      typeof window !== 'undefined' &&
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ) {
      config._retryDirect = true;
      const currentBase = config.baseURL || apiBase;
      if (currentBase === '/api/v1' || !currentBase.includes('localhost:8000')) {
        config.baseURL = 'http://localhost:8000/api/v1';
        try {
          return await axios(config);
        } catch (retryErr) {
          return Promise.reject(retryErr);
        }
      }
    }

    if (error.response && error.response.status === 401) {
      localStorage.removeItem('automind_token');
      localStorage.removeItem('automind_user');
      if (
        typeof window !== 'undefined' &&
        window.location.pathname !== '/login' &&
        window.location.pathname !== '/register' &&
        window.location.pathname !== '/'
      ) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
