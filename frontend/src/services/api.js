import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (email, password) =>
  api.post('/auth/login', { email, password });

// Users
export const getUsers = () => api.get('/users');
export const createUser = (userData) => api.post('/users', userData);
export const activateUser = (userId) => api.put(`/users/${userId}/activate`);
export const deactivateUser = (userId) => api.put(`/users/${userId}/deactivate`);

// Tickets
export const getTickets = (params = {}) => api.get('/tickets', { params });
export const getTicket = (id) => api.get(`/tickets/${id}`);
export const createTicket = (ticketData) => api.post('/tickets', ticketData);
export const updateTicketStatus = (id, status) =>
  api.put(`/tickets/${id}/status`, { status });
export const assignTicket = (id, assignedTo) =>
  api.put(`/tickets/${id}/assign`, { assigned_to: assignedTo });

// Comments
export const getComments = (ticketId) => api.get(`/tickets/${ticketId}/comments`);
export const createComment = (ticketId, commentData) =>
  api.post(`/tickets/${ticketId}/comments`, commentData);

// History
export const getHistory = (ticketId) => api.get(`/tickets/${ticketId}/history`);

// Categories
export const getCategories = () => api.get('/categories');
export const createCategory = (categoryData) => api.post('/categories', categoryData);

// Reports
export const getGeneralReport = () => api.get('/reports/general');
export const getCategoryReport = () => api.get('/reports/by-category');
export const getTechnicianReport = () => api.get('/reports/by-technician');

export default api;
