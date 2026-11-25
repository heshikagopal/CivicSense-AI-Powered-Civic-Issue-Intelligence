import axios from 'axios';
import { User, AuthResponse } from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('civicsense_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authStorage = {
  getToken: () => localStorage.getItem('civicsense_token'),
  getUser: (): User | null => {
    const raw = localStorage.getItem('civicsense_user');
    return raw ? JSON.parse(raw) : null;
  },
  setAuth: (token: string, user: User) => {
    localStorage.setItem('civicsense_token', token);
    localStorage.setItem('civicsense_user', JSON.stringify(user));
  },
  clearAuth: () => {
    localStorage.removeItem('civicsense_token');
    localStorage.removeItem('civicsense_user');
  },
};

export default api;
