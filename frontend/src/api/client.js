import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// ---------------------------------------------------------------------------
// Suppliers
// ---------------------------------------------------------------------------
export const getSuppliers = () => api.get('/api/suppliers');
export const getSupplier = (id) => api.get(`/api/suppliers/${id}`);
export const getAlternates = (id) => api.get(`/api/suppliers/${id}/alternates`);

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------
export const getEvents = (params) => api.get('/api/events', { params });
export const getEvent = (id) => api.get(`/api/events/${id}`);
export const createEvent = (data) => api.post('/api/events', data);

// ---------------------------------------------------------------------------
// Risk & Dashboard
// ---------------------------------------------------------------------------
export const getDashboard = () => api.get('/api/risk/dashboard');
export const getAssessments = () => api.get('/api/risk/assessments');
export const getAssessment = (id) => api.get(`/api/risk/assessments/${id}`);
export const analyzeEvent = (eventId) => api.post(`/api/risk/analyze/${eventId}`);

// ---------------------------------------------------------------------------
// Recovery
// ---------------------------------------------------------------------------
export const getRecoveryPlans = () => api.get('/api/recovery/plans');
export const getRecoveryPlan = (id) => api.get(`/api/recovery/plans/${id}`);
export const generateRecoveryPlan = (assessmentId) => api.post(`/api/recovery/plans/${assessmentId}/generate`);
export const approveAction = (actionId) => api.post(`/api/recovery/actions/${actionId}/approve`);
export const updateActionStatus = (actionId, status) => api.patch(`/api/recovery/actions/${actionId}/status`, { status });
export const simulateRecovery = (data) => api.post(`/api/recovery/simulate`, data);
export const compareRecovery = (assessmentId) => api.post(`/api/recovery/compare`, { assessment_id: assessmentId });
export const approveRecoveryAction = (actionId) => api.post(`/api/recovery/actions/${actionId}/approve`);

export const getBlastRadius = (assessmentId) => api.get(`/api/risk/assessments/${assessmentId}/blast-radius`);
export const getExplanation = (assessmentId) => api.get(`/api/risk/assessments/${assessmentId}/explanation`);
export const explainTradeoffs = (strategies) => api.post(`/api/recovery/explain-tradeoffs`, strategies);

// ---------------------------------------------------------------------------
// Simulation
// ---------------------------------------------------------------------------
export const getScenarios = () => api.get('/api/simulate/scenarios');
export const runScenario = (scenarioId) => api.post(`/api/simulate/scenarios/${scenarioId}/run`);
export const simulateEvent = (data) => api.post('/api/simulate/event', data);

// ---------------------------------------------------------------------------
// n8n
// ---------------------------------------------------------------------------
export const getN8nStatus = () => api.get('/api/n8n/status');
export const getN8nWorkflows = () => api.get('/api/n8n/workflows');

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------
export const getHealth = () => api.get('/api/health');

export default api;
