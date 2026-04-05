/**
 * AgentFlow Zustand Store
 * Global state management for agents, workflows, and UI state.
 */
import { create } from 'zustand';
import { agentsApi, workflowsApi, toolsApi, systemApi } from './api';

export const useStore = create((set, get) => ({
  // ─── Agents ─────────────────────────────────────
  agents: [],
  selectedAgent: null,
  agentsLoading: false,

  fetchAgents: async () => {
    set({ agentsLoading: true });
    try {
      const { data } = await agentsApi.list();
      set({ agents: data, agentsLoading: false });
    } catch (err) {
      console.error('Failed to fetch agents:', err);
      set({ agentsLoading: false });
    }
  },

  fetchAgent: async (id) => {
    try {
      const { data } = await agentsApi.get(id);
      set({ selectedAgent: data });
      return data;
    } catch (err) {
      console.error('Failed to fetch agent:', err);
      return null;
    }
  },

  createAgent: async (agentData) => {
    const { data } = await agentsApi.create(agentData);
    set((state) => ({ agents: [data, ...state.agents] }));
    return data;
  },

  deleteAgent: async (id) => {
    await agentsApi.delete(id);
    set((state) => ({
      agents: state.agents.filter((a) => a.id !== id),
    }));
  },

  // ─── Workflows ──────────────────────────────────
  workflows: [],
  workflowsLoading: false,
  executionResult: null,
  executing: false,

  fetchWorkflows: async (params) => {
    set({ workflowsLoading: true });
    try {
      const { data } = await workflowsApi.list(params);
      set({ workflows: data, workflowsLoading: false });
    } catch (err) {
      console.error('Failed to fetch workflows:', err);
      set({ workflowsLoading: false });
    }
  },

  executeWorkflow: async (agentId, input) => {
    set({ executing: true, executionResult: null });
    try {
      const { data } = await agentsApi.execute(agentId, input);
      set({ executionResult: data, executing: false });

      // Refresh workflows
      get().fetchWorkflows();
      return data;
    } catch (err) {
      set({ executing: false });
      throw err;
    }
  },

  // ─── Tools ──────────────────────────────────────
  tools: [],

  fetchTools: async () => {
    try {
      const { data } = await toolsApi.list();
      set({ tools: data });
    } catch (err) {
      console.error('Failed to fetch tools:', err);
    }
  },

  // ─── System ─────────────────────────────────────
  systemHealth: null,

  fetchHealth: async () => {
    try {
      const { data } = await systemApi.health();
      set({ systemHealth: data });
    } catch (err) {
      set({ systemHealth: { status: 'error' } });
    }
  },

  // ─── UI State ───────────────────────────────────
  currentPage: 'dashboard',
  setPage: (page) => set({ currentPage: page }),
  toasts: [],
  addToast: (toast) =>
    set((state) => ({
      toasts: [...state.toasts, { id: Date.now(), ...toast }],
    })),
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
