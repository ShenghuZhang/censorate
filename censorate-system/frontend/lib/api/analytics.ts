// frontend/lib/api/analytics.ts
import { api } from './client';

export const analyticsAPI = {
  getProjectStats: (projectId: string) => api.get<any>(`/analytics/projects/${projectId}`),
  getGlobalStats: () => api.get<any>('/analytics/global'),
  getWorkloadStats: (projectId?: string) => {
    const url = projectId ? `/analytics/workload?project_id=${projectId}` : '/analytics/workload';
    return api.get<any>(url);
  },
};
