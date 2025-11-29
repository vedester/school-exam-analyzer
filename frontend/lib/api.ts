// frontend/lib/api.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor: Add Token to every request automatically
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// 2. Response Interceptor: Handles 401 Errors (NEW!)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If the backend says "Unauthorized" (401)
    if (error.response && error.response.status === 401) {
      if (typeof window !== 'undefined') {
        // Clear the bad token
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Force redirect to login page
        // We use window.location because router.push isn't available in non-component files
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

