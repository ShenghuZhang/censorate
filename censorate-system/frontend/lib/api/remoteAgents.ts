// frontend/lib/api/remoteAgents.ts
import { api } from './client';

export interface RemoteAgent {
  id: string;
  name: string;
  agentType: string;
  endpointUrl: string;
  status: string;
  description?: string;
  capabilities: string[];
  config: Record<string, any>;
  healthCheckPath?: string;
  healthCheckInterval?: number;
  lastHealthCheck?: string;
}

type RemoteAgentApiResponse = {
  id: string;
  name: string;
  agent_type: string;
  endpoint_url: string;
  status: string;
  description?: string;
  capabilities?: string[];
  config?: Record<string, any>;
  health_check_path?: string;
  health_check_interval?: number;
  last_health_check?: string;
};

type SendMessageInput = {
  message: string;
  projectId?: string;
  threadId?: string;
  config?: Record<string, any>;
};

type SendMessageResponse = {
  response: string;
  thread_id?: string;
  threadId?: string;
  timestamp: string;
};

const serializeAgentPayload = (data: Record<string, any>) => {
  const payload: Record<string, any> = {};

  if (data.name !== undefined) payload.name = data.name;
  if (data.agentType !== undefined || data.agent_type !== undefined) payload.agent_type = data.agentType ?? data.agent_type;
  if (data.endpointUrl !== undefined || data.endpoint_url !== undefined) payload.endpoint_url = data.endpointUrl ?? data.endpoint_url;
  if (data.healthCheckPath !== undefined || data.health_check_path !== undefined) payload.health_check_path = data.healthCheckPath ?? data.health_check_path;
  if (data.healthCheckInterval !== undefined || data.health_check_interval !== undefined) payload.health_check_interval = data.healthCheckInterval ?? data.health_check_interval;
  if (data.description !== undefined) payload.description = data.description;
  if (data.capabilities !== undefined) payload.capabilities = data.capabilities;
  if (data.config !== undefined) payload.config = data.config;

  const apiKey = data.apiKey ?? data.api_key;
  if (apiKey !== undefined && apiKey !== null && String(apiKey).trim() !== '') {
    payload.api_key = apiKey;
  }

  return payload;
};

const normalizeAgent = (agent: RemoteAgentApiResponse): RemoteAgent => ({
  id: agent.id,
  name: agent.name,
  agentType: agent.agent_type,
  endpointUrl: agent.endpoint_url,
  status: agent.status,
  description: agent.description,
  capabilities: agent.capabilities || [],
  config: agent.config || {},
  healthCheckPath: agent.health_check_path,
  healthCheckInterval: agent.health_check_interval,
  lastHealthCheck: agent.last_health_check,
});

export const remoteAgentsAPI = {
  listAgents: async () => (await api.get<RemoteAgentApiResponse[]>('/remote-agents')).map(normalizeAgent),
  getAgent: async (id: string) => normalizeAgent(await api.get<RemoteAgentApiResponse>(`/remote-agents/${id}`)),
  createAgent: async (data: any) => normalizeAgent(await api.post<RemoteAgentApiResponse>('/remote-agents', serializeAgentPayload(data))),
  registerAgent: async (data: any) => normalizeAgent(await api.post<RemoteAgentApiResponse>('/remote-agents', serializeAgentPayload(data))),
  updateAgent: async (id: string, data: any) => normalizeAgent(await api.put<RemoteAgentApiResponse>(`/remote-agents/${id}`, serializeAgentPayload(data))),
  deleteAgent: (id: string) => api.delete(`/remote-agents/${id}`),
  unregisterAgent: (id: string) => api.delete(`/remote-agents/${id}`),
  checkHealth: (id: string) => api.post<any>(`/remote-agents/${id}/health`),
  sendMessage: async (id: string, data: SendMessageInput) => {
    const response = await api.post<SendMessageResponse>(`/remote-agents/${id}/chat`, {
      message: data.message,
      thread_id: data.threadId,
      project_id: data.projectId,
      config: data.config,
    });

    return {
      response: response.response,
      threadId: response.threadId || response.thread_id || '',
      timestamp: response.timestamp,
    };
  },
  streamChat: (id: string, data: SendMessageInput): EventSource => {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8216/api/v1';
    let currentToken: string | null = null;
    try {
      const s = localStorage.getItem('auth-storage');
      if (s) currentToken = JSON.parse(s).state.token;
    } catch {}
    const params = new URLSearchParams({ message: data.message });
    if (data.threadId) params.append('thread_id', data.threadId);
    if (data.projectId) params.append('project_id', data.projectId);
    if (currentToken) params.append('token', currentToken);
    return new EventSource(`${API_BASE_URL}/remote-agents/${id}/chat/stream?${params.toString()}`);
  },
  listAvailableSkills: async () => {
    return api.get<{ id: string; name: string; description: string }[]>('/remote-agents/available-skills');
  },
};
