import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/api/v1/auth/login', { email, password });
    return response.data;
  },
};

export const productsAPI = {
  getProducts: async (params = {}) => {
    const response = await api.get('/api/v1/products', { params });
    return response.data;
  },
};

export const ordersAPI = {
  createOrder: async (orderData) => {
    const response = await api.post('/api/v1/orders', orderData);
    return response.data;
  },
  getOrders: async () => {
    const response = await api.get('/api/v1/orders');
    return response.data;
  },
};

export default api;
