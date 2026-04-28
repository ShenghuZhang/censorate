'use client';

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface TeamMember {
  id: string;
  name: string;
  nickname: string;
  email?: string;
  phone?: string;
  role: string;
  avatar?: string;
  type: 'human' | 'ai';
  status: 'active' | 'inactive';
  joinedAt: string;
}

export interface AIAgent extends TeamMember {
  type: 'ai';
  agentType: string;
  skills: string[];
  memoryEnabled: boolean;
  memoryDocumentId?: string;
  deepagentConfig?: Record<string, any>;
}

interface TeamState {
  members: TeamMember[];
  aiAgents: AIAgent[];
  selectedMember: TeamMember | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchMembers: (projectId: string) => Promise<void>;
  addMember: (projectId: string, member: Omit<TeamMember, 'id' | 'joinedAt'>) => Promise<void>;
  updateMember: (id: string, updates: Partial<TeamMember>) => Promise<void>;
  removeMember: (id: string) => Promise<void>;

  // AI Agent Actions
  addAgent: (projectId: string, agent: Omit<AIAgent, 'id' | 'joinedAt' | 'type'>) => Promise<void>;
  updateAgent: (id: string, updates: Partial<AIAgent>) => Promise<void>;
  removeAgent: (id: string) => Promise<void>;
  getAgentByRole: (role: string) => AIAgent | undefined;
  checkRoleAvailability: (role: string) => boolean;

  // Agent Memory Actions
  getAgentMemory: (agentId: string) => Promise<any>;
  updateAgentMemory: (agentId: string, content: any) => Promise<void>;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8216/api/v1';

// 辅助函数：将对象的属性从 snake_case 转换为 camelCase
function snakeToCamel(obj: any): any {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => snakeToCamel(item));
  }

  return Object.keys(obj).reduce((result, key) => {
    const camelKey = key.replace(/(_\w)/g, match => match[1].toUpperCase());
    result[camelKey] = snakeToCamel(obj[key]);
    return result;
  }, {} as any);
}

// Demo team members
const demoMembers: TeamMember[] = [
  {
    id: 'user-1',
    name: 'Alice Wang',
    nickname: 'Alice',
    role: 'product_manager',
    type: 'human',
    status: 'active',
    joinedAt: new Date().toISOString(),
  },
  {
    id: 'user-2',
    name: 'Bob Chen',
    nickname: 'Bob',
    role: 'developer',
    type: 'human',
    status: 'active',
    joinedAt: new Date().toISOString(),
  },
  {
    id: 'user-3',
    name: 'Carol Li',
    nickname: 'Carol',
    role: 'designer',
    type: 'human',
    status: 'active',
    joinedAt: new Date().toISOString(),
  },
  {
    id: 'user-4',
    name: 'David Zhang',
    nickname: 'David',
    role: 'qa_engineer',
    type: 'human',
    status: 'active',
    joinedAt: new Date().toISOString(),
  },
];

export const useTeamStore = create<TeamState>()(
  devtools(
    (set, get) => ({
      members: demoMembers,
      aiAgents: [],
      selectedMember: null,
      isLoading: false,
      error: null,

      fetchMembers: async (projectId: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents`);

          if (!response.ok) {
            throw new Error(`Failed to fetch members: ${response.status}`);
          }

          const data = await response.json();

          // 转换数据格式
          const formattedData = snakeToCamel(data);

          const members = formattedData.filter((m: any) => m.type === 'human') || [];
          const agents = formattedData.filter((m: any) => m.type === 'ai') || [];

          // 处理 AI agents 特定字段
          const processedAgents: AIAgent[] = agents.map((agent: any) => ({
            ...agent,
            agentType: agent.role?.replace('_agent', '') || '',
            skills: agent.skills || [],
            memoryEnabled: agent.memoryEnabled || false,
            memoryDocumentId: agent.memoryDocumentId,
            deepagentConfig: agent.deepagentConfig || {}
          }));

          set({
            members,
            aiAgents: processedAgents,
            isLoading: false
          });
        } catch (error) {
          console.error('Failed to fetch team members:', error);
          set({
            error: 'Failed to fetch team members',
            isLoading: false
          });
        }
      },

      addMember: async (projectId: string, member: Omit<TeamMember, 'id' | 'joinedAt'>) => {
        set({ isLoading: true });
        try {
          const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...member, type: 'human' })
          });
          const newMember = await response.json();
          const formattedMember = snakeToCamel(newMember);

          set((state) => ({
            members: [...state.members, formattedMember],
            isLoading: false
          }));
        } catch (error) {
          console.error('Failed to add member:', error);
          set({
            error: 'Failed to add member',
            isLoading: false
          });
        }
      },

      addAgent: async (projectId: string, agent: Omit<AIAgent, 'id' | 'joinedAt' | 'type'>) => {
        set({ isLoading: true });
        try {
          // Check if we already have an AI agent
          const currentAgents = get().aiAgents;
          if (currentAgents.length >= 1) {
            throw new Error('Each project can only have one AI agent');
          }

          const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...agent, type: 'ai' })
          });
          const newAgent = await response.json();
          const formattedAgent = snakeToCamel(newAgent);

          set((state) => ({
            aiAgents: [...state.aiAgents, formattedAgent],
            isLoading: false
          }));
        } catch (error) {
          console.error('Failed to add AI agent:', error);
          set({
            error: error instanceof Error ? error.message : 'Failed to add AI agent',
            isLoading: false
          });
          throw error;
        }
      },

      checkRoleAvailability: (role: string) => {
        const agents = get().aiAgents;
        return !agents.some(agent => agent.role === role);
      },

      getAgentByRole: (role: string) => {
        return get().aiAgents.find(agent => agent.role === role);
      },

      updateMember: async (id: string, updates: Partial<TeamMember>) => {
        set({ isLoading: true });
        try {
          const response = await fetch(`${API_BASE_URL}/agents/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
          });
          const updated = await response.json();
          const formattedUpdated = snakeToCamel(updated);

          set((state) => ({
            members: state.members.map(m => m.id === id ? formattedUpdated : m),
            aiAgents: state.aiAgents.map(a => a.id === id ? formattedUpdated : a),
            isLoading: false
          }));
        } catch (error) {
          console.error('Failed to update member:', error);
          set({
            error: 'Failed to update member',
            isLoading: false
          });
        }
      },

      removeMember: async (id: string) => {
        set({ isLoading: true });
        try {
          await fetch(`${API_BASE_URL}/agents/${id}`, {
            method: 'DELETE'
          });

          set((state) => ({
            members: state.members.filter(m => m.id !== id),
            aiAgents: state.aiAgents.filter(a => a.id !== id),
            isLoading: false
          }));
        } catch (error) {
          console.error('Failed to remove member:', error);
          set({
            error: 'Failed to remove member',
            isLoading: false
          });
        }
      },

      updateAgent: async (id: string, updates: Partial<AIAgent>) => {
        const { updateMember } = get();
        await updateMember(id, updates);
      },

      removeAgent: async (id: string) => {
        const { removeMember } = get();
        await removeMember(id);
      },

      getAgentMemory: async (agentId: string) => {
        try {
          const response = await fetch(`${API_BASE_URL}/agents/${agentId}/memory`);
          const data = await response.json();
          return snakeToCamel(data);
        } catch (error) {
          console.error('Failed to get agent memory:', error);
          return null;
        }
      },

      updateAgentMemory: async (agentId: string, content: any) => {
        try {
          const response = await fetch(`${API_BASE_URL}/agents/${agentId}/memory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
          });
          const data = await response.json();
          return snakeToCamel(data);
        } catch (error) {
          console.error('Failed to update agent memory:', error);
          return null;
        }
      }
    })
  )
);
