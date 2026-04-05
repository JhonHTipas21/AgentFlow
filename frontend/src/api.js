/**
 * AgentFlow API Client
 * Centralized HTTP client for all backend communication.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Agents ─────────────────────────────────────────
export const agentsApi = {
  list: (params) => api.get('/agents/', { params }),
  get: (id) => api.get(`/agents/${id}`),
  create: (data) => api.post('/agents/', data),
  update: (id, data) => api.put(`/agents/${id}`, data),
  delete: (id) => api.delete(`/agents/${id}`),
  execute: (id, input, metadata) =>
    api.post(`/agents/${id}/execute`, { input, metadata }),
  status: (id) => api.get(`/agents/${id}/status`),
};

// ─── Workflows ──────────────────────────────────────
export const workflowsApi = {
  list: (params) => api.get('/workflows/', { params }),
  get: (id) => api.get(`/workflows/${id}`),
  logs: (id, params) => api.get(`/workflows/${id}/logs`, { params }),
};

// ─── Tools ──────────────────────────────────────────
export const toolsApi = {
  list: () => api.get('/tools/'),
  get: (name) => api.get(`/tools/${name}`),
};

// ─── System ─────────────────────────────────────────
export const systemApi = {
  health: () => api.get('/health'),
  ready: () => api.get('/ready'),
  info: () => api.get('/info'),
  token: () => api.post('/token'),
};

export default api;
