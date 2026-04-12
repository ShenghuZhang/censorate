# Censorate Management System - Frontend Design Document

## 1. 项目结构

```
frontend/
├── app/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Breadcrumbs.tsx
│   │   ├── kanban/
│   │   │   ├── KanbanBoard.tsx
│   │   │   ├── Swimlane.tsx
│   │   │   ├── RequirementCard.tsx
│   │   │   └── DragDropContext.tsx
│   │   ├── team/
│   │   │   ├── TeamMembersList.tsx
│   │   │   ├── MemberCard.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   ├──.tsx
│   │   │   └── AgentMemoryViewer.tsx
│   │   ├── requirement/
│   │   │   ├── RequirementDetail.tsx
│   │   │   ├── RequirementForm.tsx
│   │   │   ├── AIAnalysisPanel.tsx
│   │   │   └── TransitionDialog.tsx
│   │   └── shared/
│   │       ├── Avatar.tsx
│   │       ├── Badge.tsx
│   │       ├── IconButton.tsx
│   │       └── StatusBadge.tsx
│   ├── hooks/
│   │   ├── useProject.ts
│   │   ├── useRequirements.ts
│   │   ├── useTeamMembers.ts
│   │   └── useAIAgents.ts
│   ├── stores/
│   │   ├── projectStore.ts
│   │   ├── requirementStore.ts
│   │   ├── teamStore.ts
│   │   └── agentStore.ts
│   └── pages/
│       ├── LandingPage.tsx
│       ├── KanbanPage.tsx
│       ├── BacklogPage.tsx
│       ├── TeamPage.tsx
│       └── SettingsPage.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts
│   │   ├── projects.ts
│   │   ├── requirements.ts
│   │   ├── team.ts
│   │   └── agents.ts
│   ├── state-management/
│   │   └── zustand.ts
│   └── utils/
│       ├── drag-drop.ts
│       └── formatting.ts
└── public/
```

## 2. 状态管理设计 (Zustand)

### 团队成员 Store

```typescript
// app/stores/teamStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface TeamMember {
  id: string;
  name: string;
  nickname: string;
  email?: string;
  phone?: string;
  role: string;
  avatar?: string;
  type: 'human' | 'ai';
  status: 'active' | 'inactive';
  joinedAt: Date;
}

interface AIAgent extends TeamMember {
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
  addMember: (member: Omit<TeamMember, 'id'>) => Promise<void>;
  updateMember: (id: string, updates: Partial<TeamMember>) => Promise<void>;
  removeMember: (id: string) => Promise<void>;

  // AI Agent Actions
  addAgent: (agent: Omit<AIAgent, 'id'>) => Promise<void>;
  updateAgent: (id: string, updates: Partial<AIAgent>) => Promise<void>;
  removeAgent: (id: string) => Promise<void>;
  getAgentByRole: (role: string) => AIAgent | undefined;
  checkRoleAvailability: (role: string) => boolean;

  // Agent Memory Actions
  getAgentMemory: (agentId: string) => Promise<any>;
  updateAgentMemory: (agentId: string, content: any) => Promise<void>;
}

export const useTeamStore = create<TeamState>()(
  devtools(
    (set, get) => ({
      members: [],
      aiAgents: [],
      selectedMember: null,
      isLoading: false,
      error: null,

      fetchMembers: async (projectId: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`/api/v1/projects/${projectId}/team`);
          const data = await response.json();

          const members = data.members || [];
          const agents = data.aiAgents || [];

          set({ members, aiAgents: agents, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to fetch team members', isLoading: false });
        }
      },

      addMember: async (member) => {
        set({ isLoading: true });
        try {
          const response = await fetch('/api/v1/projects/${get().currentProjectId}/team', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...member, type: 'human' })
          });
          const newMember = await response.json();

          set((state) => ({
            members: [...state.members, newMember],
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to add member', isLoading: false });
        }
      },

      addAgent: async (agent) => {
        set({ isLoading: true });
        try {
          const response = await fetch('/api/v1/projects/${get().currentProjectId}/agents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...agent, type: 'ai' })
          });
          const newAgent = await response.json();

          set((state) => ({
            aiAgents: [...state.aiAgents, newAgent],
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to add AI agent', isLoading: false });
        }
      },

      checkRoleAvailability: (role: string) => {
        const agents = get().aiAgents;
        return !agents.some(agent => agent.role === role);
      },

      getAgentByRole: (role: string) => {
        return get().aiAgents.find(agent => agent.role === role);
      },

      // ... 其他 actions
    })
  )
);
```

### 需求状态 Store

```typescript
// app/stores/requirementStore.ts
interface Requirement {
  id: string;
  projectId: string;
  reqNumber: number;
  title: string;
  description?: string;
  status: RequirementStatus;
  priority: Priority;
  source?: string;
  sourceMetadata?: any;

  // 飞书集成
  larkDocToken?: string;
  larkDocUrl?: string;
  larkEditable: boolean;

  // AI 相关
  aiSuggestions?: any;
  currentAgent?: string;
  aiConfidence?: number;

  // 返回标记
  returnCount: number;
  lastReturnedAt?: Date;

  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  assignedTo?: string;
}

interface RequirementState {
  requirements: Requirement[];
  selectedRequirement: Requirement | null;
  isLoading: boolean;
  error: string | null;

  fetchRequirements: (projectId: string) => Promise<void>;
  createRequirement: (data: Partial<Requirement>) => Promise<void>;
  updateRequirement: (id: string, updates: Partial<Requirement>) => Promise<void>;
  transitionRequirement: (id: string, toStatus: string, aiApproved: boolean) => Promise<void>;
  aiAnalyzeRequirement: (id: string) => Promise<void>;
  getRequirementsByStatus: (status: RequirementStatus) => Requirement[];
}

export const useRequirementStore = create<RequirementState>()((set, get) => ({
  requirements: [],
  selectedRequirement: null,
  isLoading: false,
  error: null,

  fetchRequirements: async (projectId: string) => {
    set({ isLoading: true });
    try {
      const response = await fetch(`/api/v1/projects/${projectId}/requirements`);
      const data = await response.json();
      set({ requirements: data, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch requirements', isLoading: false });
    }
  },

  transitionRequirement: async (id: string, toStatus: string, aiApproved: boolean) => {
    try {
      const response = await fetch(`/api/v1/requirements/${id}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ toStatus, aiApproved })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
      }

      const updated = await response.json();

      set((state) => ({
        requirements: state.requirements.map(req =>
          req.id === id ? updated : req
        ),
        selectedRequirement: updated
      }));
    } catch (error) {
      throw error;
    }
  },

  // ... 其他 actions
}));
```

## 3. 核心组件设计

### 3.1 团队管理页面

```tsx
// app/pages/TeamPage.tsx
'use client';

import { useState } from 'react';
import { useTeamStore } from '@/stores/teamStore';
import MemberCard from '@/components/team/MemberCard';
import AddMemberDialog from '@/components/team/AddMemberDialog';
import AddAgentDialog from '@/components/team/AddAgentDialog';

export default function TeamPage() {
  const { members, aiAgents, isLoading, fetchMembers, addMember, addAgent } = useTeamStore();
  const [showAddMember, setShowAddMember] = useState(false);
  const [showAddAgent, setShowAddAgent] = useState(false);

  useEffect(() => {
    fetchMembers(currentProjectId);
  }, []);

  return (
    <div className="min-h-screen bg-surface">
      <Header />
      <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold font-headline">Team Members</h1>
          <div className="flex gap-4">
            <button
              onClick={() => setShowAddMember(true)}
              className="bg-primary text-white px-6 py-3 rounded-lg font-semibold"
            >
              + Add Member
            </button>
            <button
              onClick={() => setShowAddAgent(true)}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold"
            >
              + Add AI Agent
            </button>
          </div>
        </div>

        {/* 人类成员列表 */}
        <section className="mb-12">
          <h2 className="text-xl font-bold mb-6 font-headline">Team Members</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {members.map(member => (
              <MemberCard
                key={member.id}
                member={member}
                type="human"
              />
            ))}
          </div>
        </section>

        {/* AI Agent 列表 */}
        <section>
          <h2 className="text-xl font-bold mb-6 font-headline">AI Agents</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {aiAgents.map(agent => (
              <AgentCard
                key={agent.id}
                agent={agent}
              />
            ))}
          </div>
        </section>
      </div>

      <AddMemberDialog
        isOpen={showAddMember}
        onClose={() => setShowAddMember(false)}
        onAdd={addMember}
      />

      <AddAgentDialog
        isOpen={showAddAgent}
        onClose={() => setShowAddAgent(false)}
        onAdd={addAgent}
        existingRoles={aiAgents.map(a => a.role)}
      />
    </div>
  );
}
```

### 3.2 添加 AI Agent 对话框

```tsx
// app/components/team/AddAgentDialog.tsx
import { useState } from 'react';
import { Dialog } from '@headlessui/react';

interface AddAgentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (agent: any) => Promise<void>;
  existingRoles: string[];
}

export default function AddAgentDialog({ isOpen, onClose, onAdd, existingRoles }: AddAgentDialogProps) {
  const [name, setName] = useState('');
  const [nickname, setNickname] = useState('');
  const [role, setRole] = useState('');
  const [skills, setSkills] = useState<string[]>([]);
  const [memoryEnabled, setMemoryEnabled] = useState(true);

  // 角色选项
  const availableRoles = [
    'analysis_agent',
    'design_agent',
    'development_agent',
    'testing_agent',
    'review_agent'
  ].filter(r => !existingRoles.includes(r));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await onAdd({
      name,
      nickname,
      role,
      type: 'ai',
      skills,
      memoryEnabled,
      deepagentConfig: {
        // DeepAgent 配置将根据 AGENT.MD 生成
      }
    });

    onClose();
  };

  return (
    <Dialog open={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Agent Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="e.g., Analysis Agent"
            className="w-full px-4 py-3 border rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Nickname</label>
          <input
            type="text"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="e.g., Alex"
            className="w-full px-4 py-3 border rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Role</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            required
            className="w-full px-4 py-3 border rounded-lg"
          >
            <option value="">Select role...</option>
            {availableRoles.map(r => (
              <option key={r} value={r}>
                {r.replace('_', ' ').replace(' agent', '').toUpperCase()}
              </option>
            ))}
          </select>
          {existingRoles.length === availableRoles.length && (
            <p className="text-sm text-error mt-1">
              All agent roles are already assigned
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Skills</label>
          <input
            type="text"
            placeholder="Enter skills separated by commas"
            onChange={(e) => setSkills(e.target.value.split(','))}
            className="w-full px-4 py-3 border rounded-lg"
          />
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="memory-enabled"
            checked={memoryEnabled}
            onChange={(e) => setMemoryEnabled(e.target.checked)}
            className="w-5 h-5"
          />
          <label htmlFor="memory-enabled" className="text-sm">
            Enable Long-term Memory (local document)
          </label>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-3 border rounded-lg"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!role || !name}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold disabled:opacity-50"
          >
            Add AI Agent
          </button>
        </div>
      </form>
    </Dialog>
  );
}
```

### 3.3 AI Agent 卡片组件

```tsx
// app/components/team/AgentCard.tsx
import { useState } from 'react';
import AgentMemoryViewer from './AgentMemoryViewer';

interface AgentCardProps {
  agent: AIAgent;
}

export default function AgentCard({ agent }: AgentCardProps) {
  const [showMemory, setShowMemory] = useState(false);

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'analysis_agent': return 'bg-amber-100 text-amber-800';
      case 'design_agent': return 'bg-blue-100 text-blue-800';
      case 'development_agent': return 'bg-emerald-100 text-emerald-800';
      case 'testing_agent': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow group">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-2xl">
            <span className="material-symbols-outlined">smart_toy</span>
          </div>
          <div>
            <h3 className="font-bold text-lg font-headline">{agent.nickname}</h3>
            <p className="text-sm text-secondary">{agent.name}</p>
          </div>
        </div>
        <span className={`text-xs font-bold px-3 py-1 rounded-full ${getRoleBadgeColor(agent.role)}`}>
          {agent.role.replace('_', ' ').replace(' agent', '').toUpperCase()}
        </span>
      </div>

      {/* Details */}
      <div className="space-y-3 mb-6">
        {agent.skills.length > 0 && (
          <div>
            <p className="text-xs font-medium text-secondary mb-2 uppercase tracking-wider">Skills</p>
            <div className="flex flex-wrap gap-2">
              {agent.skills.map((skill, index) => (
                <span key={index} className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        <div>
          <p className="text-xs font-medium text-secondary mb-2 uppercase tracking-wider">Memory</p>
          <div className="flex items-center gap-2">
            <span className={`w-3 h-3 rounded-full ${agent.memoryEnabled ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className="text-sm">
              {agent.memoryEnabled ? 'Enabled (Local Document)' : 'Disabled'}
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center pt-4 border-t">
        <div className="text-xs text-secondary">
          Joined {new Date(agent.joinedAt).toLocaleDateString()}
        </div>
        <div className="flex gap-2">
          {agent.memoryEnabled && (
            <button
              onClick={() => setShowMemory(true)}
              className="text-sm text-primary hover:underline"
            >
              View Memory
            </button>
          )}
          <button className="p-2 hover:bg-gray-100 rounded">
            <span className="material-symbols-outlined text-lg">settings</span>
          </button>
        </div>
      </div>

      {/* Memory Viewer Dialog */}
      {showMemory && (
        <AgentMemoryViewer
          agent={agent}
          onClose={() => setShowMemory(false)}
        />
      )}
    </div>
  );
}
```

### 3.4 Agent Memory 查看器

```tsx
// app/components/team/AgentMemoryViewer.tsx
import { useState, useEffect } from 'react';

interface AgentMemoryViewerProps {
  agent: AIAgent;
  onClose: () => void;
}

export default function AgentMemoryViewer({ agent, onClose }: AgentMemoryViewerProps) {
  const [memory, setMemory] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadMemory();
  }, [agent.id]);

  const loadMemory = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/agents/${agent.id}/memory`);
      const data = await response.json();
      setMemory(data);
    } catch (error) {
      console.error('Failed to load agent memory:', error);
    }
    setIsLoading(false);
  };

  return (
    <Dialog open onClose={onClose} className="max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold font-headline">{agent.nickname} Memory</h2>
          <p className="text-sm text-secondary">
            Long-term memory stored locally as document
          </p>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-primary rounded-full border-t-transparent" />
        </div>
      ) : memory ? (
        <div className="bg-gray-50 rounded-lg p-6 max-h-[500px] overflow-y-auto">
          <pre className="text-sm whitespace-pre-wrap">
            {JSON.stringify(memory, null, 2)}
          </pre>
        </div>
      ) : (
        <div className="text-center py-12 text-secondary">
          <p>No memory data available</p>
        </div>
      )}
    </Dialog>
  );
}
```

### 3.5 Kanban 看板组件

```tsx
// app/components/kanban/KanbanBoard.tsx
import { DndProvider, useDrop } from 'react-dnd';
import { useRequirementStore } from '@/stores/requirementStore';
import Swimlane from './Swimlane';

const SWIMLANES = [
  { id: 'new', title: 'New Requirement', color: 'bg-gray-50' },
  { id: 'analysis', title: 'Analysis', color: 'bg-amber-50' },
  { id: 'design',', title: 'Design', color: 'bg-blue-50' },
  { id: 'development', title: 'Development', color: 'bg-emerald-50' },
  { id: 'testing', title: 'Testing', color: 'bg-purple-50' },
  { id: 'completed', title: 'Completed', color: 'bg-green-50' },
];

export default function KanbanBoard() {
  const { requirements, transitionRequirement } = useRequirementStore();

  const getRequirementsByStatus = (status: string) => {
    return requirements.filter(req => req.status === status);
  };

  const handleDrop = async (reqId: string, targetStatus: string) => {
    const req = requirements.find(r => r.id === requestId);
    if (!req || req.status === targetStatus) return;

    // 检查是否需要 AI 批准
    const requiresAIApproval = isForwardTransition(req.status, targetStatus);

    if (requiresAIApproved) {
      // 显示 AI 批准对话框
      showAITransitionDialog(reqId, targetStatus);
    } else {
      // 向后拖拽，直接转换
      await transitionRequirement(reqId, targetStatus, false);
    }
  };

  return (
    <DndProvider>
      <div className="flex gap-6 overflow-x-auto p-8 min-h-[calc(100vh-4rem)]">
        {SWIMLANES.map(lane => (
          <Swimlane
            key={lane.id}
            lane={lane}
            requirements={getRequirementsByStatus(lane.id)}
            onDrop={handleDrop}
          />
        ))}
      </div>
    </DndProvider>
  );
}
```

### 3.6 需求卡片组件

```tsx
// app/components/kanban/RequirementCard.tsx
import { useDrag } from 'react-dnd';
import { useState } from 'react';
import RequirementDetail from '../requirement/RequirementDetail';

interface RequirementCardProps {
  requirement: Requirement;
}

export default function RequirementCard({ requirement }: RequirementCardProps) {
  const [showDetail, setShowDetail] = useState(false);

  const [{ isDragging }, drag] = useDrag({
    type: 'REQUIREMENT',
    item: { id: requirement.id },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  });

  return (
    <>
      <div
        ref={drag}
        onClick={() => setShowDetail(true)}
        className={`
          bg-white rounded-xl p-4 shadow-sm hover:shadow-md
          transition-shadow cursor-pointer
          ${isDragging ? 'opacity-50' : 'opacity-100'}
        `}
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          <span className="bg-gray-100 text-xs font-bold px-2 py-1 rounded-full">
            REQ-{requirement.reqNumber}
          </span>

          {/* 返回标记 */}
          {requirement.returnCount > 0 && (
            <div className="flex items-center gap-1 bg-red-50 text-red-700 text-xs font-bold px-2 py-1 rounded-full">
              <span className="material-symbols-outlined">undo</span>
              RETURNED ({requirement.returnCount})
            </div>
          )}

          {/* AI 状态 */}
          {require.aiConfidence && (
            <div className="flex items-center gap-1 bg-blue-50 text-blue-700 text-xs font-bold px-2 py-1 rounded-full">
              <span className="material-symbols-outlined">auto_awesome</span>
              AI CONFIDENCE: {Math.round(requirement.aiConfidence * 100)}%
            </div>
          )}
        </div>

        {/* Title */}
        <h4 className="font-semibold text-sm mb-4 leading-snug">
          {requirement.title}
        </h4>

        {/* Description */}
        {requirement.description && (
          <p className="text-sm text-secondary mb-4 line-clamp-3">
            {requirement.description}
          </p>
        )}

        {/* 飞书文档链接 */}
        {requirement.larkDocUrl && (
          <div className="flex items-center gap-2 mb-4">
            <span className="material-symbols-outlined text-blue-500">description</span>
            <a
              href={requirement.larkDocUrl}
              target="_blank"
              className="text-sm text-blue-600 hover:underline"
            >
              {requirement.larkEditable ? 'Edit in Feishu' : 'View Document'}
            </a>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-between items-center pt-3 border-t">
          <div className="flex items-center gap-2">
            {/* 分配给 */}
            {requirement.assignedTo && (
              <img
                src={getAvatarUrl(requirement.assignedTo)}
                alt="Assignee"
                className="w-6 h-6 rounded-full"
              />
            )}

            {/* 当前 AI Agent */}
            {requirement.currentAgent && (
              <div className="flex items-center gap-1 text-xs text-secondary">
                <span className="material-symbols-outlined text-purple-500">smart_toy</span>
                {requirement.currentAgent}
              </div>
            )}
          </div>

          {/* 优先级 */}
          <span className={`text-xs font-bold px-2 py-1 rounded-full ${getPriorityColor(requirement.priority)}`}>
            {requirement.priority.toUpperCase()}
          </span>
        </div>
      </div>

      {/* 详情对话框 */}
      {showDetail && (
        <RequirementDetail
          requirement={requirement}
          onClose={() => setShowDetail(false)}
        />
      )}
    </>
  );
}
```

## 4. API 客户端

```typescript
// lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private baseUrl: string;
  private token: string | null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  }

  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` })
    };
  }

  async get(endpoint: string) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async post(endpoint: string, data: any) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async put(endpoint: string, data: any) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async delete(endpoint: string) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }
}

export const api = new APIClient(API_BASE_URL);
```

## 5. 自定义 Hooks

```typescript
// app/hooks/useAIAgents.ts
import { useTeamStore } from '@/stores/teamStore';

export function useAIAgents() {
  const { aiAgents, addAgent, updateAgent, removeAgent, getAgentByRole } = useTeamStore();

  const getAnalysisAgent = () => getAgentByRole('analysis_agent');
  const getDesignAgent = () => getAgentByRole('design_agent');
  const getDevelopmentAgent = () => getAgentByRole('development_agent');
  const getTestingAgent = () => getAgentByRole('testing_agent');

  return {
    agents: aiAgents,
    addAgent,
    updateAgent,
    removeAgent,
    getAgentByRole,
    getAnalysisAgent,
    getDesignAgent,
    getDevelopmentAgent,
    getTestingAgent
  };
}
```

## 6. 路由配置

```typescript
// app/app.tsx
import KanbanPage from './pages/KanbanPage';
import BacklogPage from './pages/BacklogPage';
import TeamPage from './pages/TeamPage';
import SettingsPage from './pages/SettingsPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: 'projects/:projectId/kanban', element: <KanbanPage /> },
      { path: 'projects/:projectId/backlog', element: <BacklogPage /> },
      { path: 'projects/:projectId/team', element: <TeamPage /> },
      { path: 'projects/:projectId/settings', element: <SettingsPage /> },
    ]
  }
]);
```

## 7. 样式系统

```css
/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        headline: ['Manrope', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        label: ['Inter', 'sans-serif']
      },
      colors: {
        'surface': '#f8f9fa',
        'primary': '#0040a1',
        'primary-container': '#0056d2',
        'secondary': '#4f5f77',
        'error': '#ba1a1a',
        'on-surface': '#191c1d',
        'on-secondary-container': '#54647b'
      }
    }
  }
}
```

## 8. 性能优化

- **代码分割**: 使用 React.lazy() 按路由分割代码
- **虚拟滚动**: 长列表使用 react-window 或 react-virtualized
- **请求缓存**: 使用 React Query 的缓存功能
- **图片优化**: 使用 Next.js Image 组件自动优化
- **CSS 优化**: 使用 Tailwind CSS 的 JIT 模式

## 9. 可访问性 (A11y)

- 语义化 HTML 标签
- ARIA 标签和角色
- 键盘导航支持
- 屏幕阅读器友好
- WCAG 2.1 AA 标准
```

## 10. 参考页面映射

| 功能 | 参考文件 | 说明 |
|------|----------|------|
| 项目列表 | landing.html | 项目卡片布局、状态标签 |
| 看板 | kanban.html | 泳道、拖放、卡片 |
| 待办事项 | backlog.html | 列表视图、筛选排序 |
| 团队设置 | settings.html | 成员管理、角色配置 |

## 11. DeepAgent 集成配置

```typescript
// lib/deepagent/config.ts
interface DeepAgentConfig {
  agentType: string;
  model: string;
  temperature: number;
  maxTokens: number;
  tools?: Tool[];
  systemPrompt?: string;
  memoryConfig?: {
    enabled: boolean;
    documentPath: string;
    maxContextLength: number;
  };
}

export const getDeepAgentConfig = (agentType: string): DeepAgentConfig => {
  const configs: Record<string, DeepAgentConfig> = {
    analysis_agent: {
      agentType: 'analysis_agent',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.3,
      maxTokens: 4096,
      tools: ['text-analysis', 'duplicate-detection'],
     '    },
    design_agent: {
      agentType: 'design_agent',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.7,
      maxTokens: 8192,
      tools: ['design-generation', 'ui-prototyping'],
      systemPrompt: 'You are an expert UI/UX design agent...'
    },
    development_agent: {
      agentType: 'development_agent',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.5,
      maxTokens: 8192,
      tools: ['code-generation', 'code-review'],
    },
    testing_agent: {
      agentType: 'testing_agent',
      model: 'claude-3-5-sonnet-20240620',
      temperature: 0.2,
      maxTokens: 4096,
      tools: ['test-generation', 'test-execution'],
    }
  };

  return configs[agentType];
};
```
