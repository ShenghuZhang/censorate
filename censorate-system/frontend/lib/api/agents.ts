// frontend/lib/api/agents.ts
import { api } from './client';

export interface Agent {
  id: string;
  project_id: string;
  name: string;
  nickname: string;
  email?: string;
  role?: string;
  type: string;
  avatar_url?: string;
  status: string;
  joined_at: string;
  skills: string[];
  memory_enabled: boolean;
  memory_document_id?: string;
  created_at: string;
  updated_at: string;
}

export interface AgentCreate {
  name: string;
  nickname: string;
  role: string;
  skills?: string[];
  memory_enabled?: boolean;
}

export interface AgentUpdate {
  name?: string;
  nickname?: string;
  status?: string;
  skills?: string[];
  memory_enabled?: boolean;
  deepagent_config?: Record<string, any>;
}

export const agentsAPI = {
  list: (projectId?: string): Promise<Agent[]> => {
    const url = projectId ? `/agents?project_id=${projectId}` : '/agents';
    return api.get<Agent[]>(url);
  },
  get: (id: string) => api.get<Agent>(`/agents/${id}`),
  create: (data: AgentCreate) => api.post<Agent>('/agents', data),
  update: (id: string, data: AgentUpdate) => api.put<Agent>(`/agents/${id}`, data),
  delete: (id: string) => api.delete(`/agents/${id}`),
  getMemory: (id: string) => api.get<any>(`/agents/${id}/memory`),
  clearMemory: (id: string) => api.post<any>(`/agents/${id}/memory/clear`),
};
