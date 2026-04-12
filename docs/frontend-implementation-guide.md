# Stratos Management System - Frontend Implementation Guide

## Overview

This guide provides a step-by-step implementation for the Stratos Management System frontend, following the design specifications. We'll build a modern, AI-native requirement management system using Next.js 14, TypeScript, Tailwind CSS, and shadcn/ui.

## Prerequisites

- Node.js 18+
- npm or yarn
- Git

## 1. Project Setup

### 1.1 Create Next.js Project

```bash
# Create a new Next.js 14 project with TypeScript
npx create-next-app@latest stratos-frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

cd stratos-frontend
```

### 1.2 Install Dependencies

```bash
# Install shadcn/ui
npx shadcn-ui@latest init

# Install required components
npx shadcn-ui@latest add button card dialog input label select separator

# Install additional libraries
npm install zustand react-dnd react-dnd-html5-backend @headlessui/react lucide-react
```

### 1.3 Project Structure

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
│   │   │   ├── AddMemberDialog.tsx
│   │   │   ├── AddAgentDialog.tsx
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

## 2. Core Layout and Navigation

### 2.1 Sidebar Component

```tsx
// app/components/layout/Sidebar.tsx
'use client';

import { useState } from 'react';
import { LayoutDashboard, KanbanSquare, Users, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'kanban', label: 'Kanban Board', icon: KanbanSquare },
  { id: 'team', label: 'Team Management', icon: Users },
  { id: 'settings', label: 'Settings', icon: Settings },
];

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <div className="p-6">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">S</span>
          </div>
          <h1 className="text-xl font-bold font-headline">Stratos</h1>
        </div>

        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <Button
                key={item.id}
                variant={activeTab === item.id ? 'default' : 'ghost'}
                className={cn(
                  'w-full justify-start gap-3',
                  activeTab === item.id 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:text-gray-900'
                )}
                onClick={() => onTabChange(item.id)}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
```

### 2.2 Header Component

```tsx
// app/components/layout/Header.tsx
'use client';

import { Bell, User } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  projectName?: string;
  onNotificationClick?: () => void;
  onProfileClick?: () => void;
}

export default function Header({ 
  projectName = 'My Project', 
  onNotificationClick, 
  onProfileClick 
}: HeaderProps) {
  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold font-headline">{projectName}</h2>
      </div>

      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={onNotificationClick}
          className="relative"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full"></span>
        </Button>

        <Button 
          variant="ghost" 
          size="icon" 
          onClick={onProfileClick}
        >
          <User className="w-5 h-5" />
        </Button>
      </div>
    </header>
  );
}
```

### 2.3 Layout Component

```tsx
// app/components/layout/Layout.tsx
'use client';

import { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [activeTab, setActiveTab] = useState('kanban');

  return (
    <div className="min-h-screen bg-surface">
      <div className="flex">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
```

## 3. State Management

### 3.1 Team Store

```typescript
// app/stores/teamStore.ts
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
  joinedAt: Date;
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

  fetchMembers: (projectId: string) => Promise<void>;
  addMember: (member: Omit<TeamMember, 'id'>) => Promise<void>;
  updateMember: (id: string, updates: Partial<TeamMember>) => Promise<void>;
  removeMember: (id: string) => Promise<void>;

  addAgent: (agent: Omit<AIAgent, 'id'>) => Promise<void>;
  updateAgent: (id: string, updates: Partial<AIAgent>) => Promise<void>;
  removeAgent: (id: string) => Promise<void>;
  getAgentByRole: (role: string) => AIAgent | undefined;
  checkRoleAvailability: (role: string) => boolean;

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
          const response = await fetch(`/api/v1/projects/${get().currentProjectId}/team`, {
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
          const response = await fetch(`/api/v1/projects/${get().currentProjectId}/agents`, {
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

      getAgentMemory: async (agentId: string) => {
        try {
          const response = await fetch(`/api/v1/agents/${agentId}/memory`);
          return await response.json();
        } catch (error) {
          console.error('Failed to load agent memory:', error);
          return null;
        }
      },

      updateAgentMemory: async (agentId: string, content: any) => {
        try {
          await fetch(`/api/v1/agents/${agentId}/memory`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(content)
          });
        } catch (error) {
          console.error('Failed to update agent memory:', error);
        }
      },

      updateMember: async (id: string, updates: Partial<TeamMember>) => {
        set({ isLoading: true });
        try {
          const response = await fetch(`/api/v1/members/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
          });
          const updatedMember = await response.json();

          set((state) => ({
            members: state.members.map(member => 
              member.id === id ? updatedMember : member
            ),
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to update member', isLoading: false });
        }
      },

      removeMember: async (id: string) => {
        set({ isLoading: true });
        try {
          await fetch(`/api/v1/members/${id}`, {
            method: 'DELETE'
          });

          set((state) => ({
            members: state.members.filter(member => member.id !== id),
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to remove member', isLoading: false });
        }
      },

      updateAgent: async (id: string, updates: Partial<AIAgent>) => {
        set({ isLoading: true });
        try {
          const response = await fetch(`/api/v1/agents/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
          });
          const updatedAgent = await response.json();

          set((state) => ({
            aiAgents: state.aiAgents.map(agent => 
              agent.id === id ? updatedAgent : agent
            ),
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to update AI agent', isLoading: false });
        }
      },

      removeAgent: async (id: string) => {
        set({ isLoading: true });
        try {
          await fetch(`/api/v1/agents/${id}`, {
            method: 'DELETE'
          });

          set((state) => ({
            aiAgents: state.aiAgents.filter(agent => agent.id !== id),
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to remove AI agent', isLoading: false });
        }
      }
    })
  )
);
```

### 3.2 Requirement Store

```typescript
// app/stores/requirementStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type RequirementStatus = 
  | 'new' 
  | 'analysis' 
  | 'design' 
  | 'development' 
  | 'testing' 
  | 'completed';

export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export interface Requirement {
  id: string;
  projectId: string;
  reqNumber: number;
  title: string;
  description?: string;
  status: RequirementStatus;
  priority: Priority;
  source?: string;
  sourceMetadata?: any;

  larkDocToken?: string;
  larkDocUrl?: string;
  larkEditable: boolean;

  aiSuggestions?: any;
  currentAgent?: string;
  aiConfidence?: number;

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

export const useRequirementStore = create<RequirementState>()(
  devtools(
    (set, get) => ({
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

      createRequirement: async (data: Partial<Requirement>) => {
        set({ isLoading: true });
        try {
          const response = await fetch('/api/v1/requirements', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          });
          const newRequirement = await response.json();

          set((state) => ({
            requirements: [...state.requirements, newRequirement],
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to create requirement', isLoading: false });
        }
      },

      updateRequirement: async (id: string, updates: Partial<Requirement>) => {
        set({ isLoading: true });
        try {
          const response = await fetch(`/api/v1/requirements/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
          });
          const updated = await response.json();

          set((state) => ({
            requirements: state.requirements.map(req =>
              req.id === id ? updated : req
            ),
            selectedRequirement: state.selectedRequirement?.id === id ? updated : state.selectedRequirement,
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to update requirement', isLoading: false });
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

      aiAnalyzeRequirement: async (id: string) => {
        set({ isLoading: true });
        try {
          const response = await fetch(`/api/v1/requirements/${id}/ai-analyze`, {
            method: 'POST'
          });
          const updated = await response.json();

          set((state) => ({
            requirements: state.requirements.map(req =>
              req.id === id ? updated : req
            ),
            selectedRequirement: state.selectedRequirement?.id === id ? updated : state.selectedRequirement,
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to analyze requirement', isLoading: false });
        }
      },

      getRequirementsByStatus: (status: RequirementStatus) => {
        return get().requirements.filter(req => req.status === status);
      }
    })
  )
);
```

## 4. Kanban Board (Core Feature)

### 4.1 Kanban Board Component

```tsx
// app/components/kanban/KanbanBoard.tsx
'use client';

import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useRequirementStore } from '@/stores/requirementStore';
import Swimlane from './Swimlane';

const SWIMLANES = [
  { id: 'new', title: 'New Requirement', color: 'bg-gray-50' },
  { id: 'analysis', title: 'Analysis', color: 'bg-amber-50' },
  { id: 'design', title: 'Design', color: 'bg-blue-50' },
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
    const req = requirements.find(r => r.id === reqId);
    if (!req || req.status === targetStatus) return;

    try {
      await transitionRequirement(reqId, targetStatus, false);
    } catch (error) {
      console.error('Failed to transition requirement:', error);
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
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

### 4.2 Swimlane Component

```tsx
// app/components/kanban/Swimlane.tsx
'use client';

import { useDrop } from 'react-dnd';
import RequirementCard from './RequirementCard';

interface SwimlaneProps {
  lane: { id: string; title: string; color: string };
  requirements: any[];
  onDrop: (reqId: string, targetStatus: string) => void;
}

export default function Swimlane({ lane, requirements, onDrop }: SwimlaneProps) {
  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'REQUIREMENT',
    drop: (item: { id: string }) => {
      onDrop(item.id, lane.id);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  }));

  return (
    <div 
      ref={drop}
      className={`
        min-w-[320px] rounded-xl p-4
        ${isOver ? 'bg-blue-100' : lane.color}
      `}
    >
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-bold text-lg font-headline">{lane.title}</h3>
        <span className="bg-white/50 text-sm font-semibold px-2 py-1 rounded-full">
          {requirements.length}
        </span>
      </div>

      <div className="space-y-4">
        {requirements.map(req => (
          <RequirementCard
            key={req.id}
            requirement={req}
          />
        ))}
      </div>

      {requirements.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-sm">No requirements</p>
        </div>
      )}
    </div>
  );
}
```

### 4.3 Requirement Card Component

```tsx
// app/components/kanban/RequirementCard.tsx
'use client';

import { useDrag } from 'react-dnd';
import { useState } from 'react';
import { User } from 'lucide-react';
import RequirementDetail from '../requirement/RequirementDetail';

interface RequirementCardProps {
  requirement: any;
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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
        <div className="flex justify-between items-start mb-3">
          <span className="bg-gray-100 text-xs font-bold px-2 py-1 rounded-full">
            REQ-{requirement.reqNumber}
          </span>

          {requirement.returnCount > 0 && (
            <div className="flex items-center gap-1 bg-red-50 text-red-700 text-xs font-bold px-2 py-1 rounded-full">
              <span className="material-symbols-outlined text-sm">undo</span>
              RETURNED ({requirement.returnCount})
            </div>
          )}
        </div>

        <h4 className="font-semibold text-sm mb-4 leading-snug">
          {requirement.title}
        </h4>

        {requirement.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-3">
            {requirement.description}
          </p>
        )}

        {requirement.larkDocUrl && (
          <div className="flex items-center gap-2 mb-4">
            <span className="material-symbols-outlined text-blue-500 text-sm">description</span>
            <a
              href={requirement.larkDocUrl}
              target="_blank"
              className="text-sm text-blue-600 hover:underline"
            >
              {requirement.larkEditable ? 'Edit in Feishu' : 'View Document'}
            </a>
          </div>
        )}

        <div className="flex justify-between items-center pt-3 border-t">
          <div className="flex items-center gap-2">
            {requirement.assignedTo && (
              <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center">
                <User className="w-4 h-4" />
              </div>
            )}

            {requirement.currentAgent && (
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <span className="material-symbols-outlined text-purple-500 text-sm">smart_toy</span>
                {requirement.currentAgent}
              </div>
            )}
          </div>

          <span className={`text-xs font-bold px-2 py-1 rounded-full ${getPriorityColor(requirement.priority)}`}>
            {requirement.priority.toUpperCase()}
          </span>
        </div>
      </div>

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

## 5. Team Management

### 5.1 Team Page

```tsx
// app/components/team/TeamPage.tsx
'use client';

import { useState, useEffect } from 'react';
import { useTeamStore } from '@/stores/teamStore';
import MemberCard from './MemberCard';
import AgentCard from './AgentCard';
import AddMemberDialog from './AddMemberDialog';
import AddAgentDialog from './AddAgentDialog';

export default function TeamPage() {
  const { members, aiAgents, isLoading, fetchMembers, addMember, addAgent } = useTeamStore();
  const [showAddMember, setShowAddMember] = useState(false);
  const [showAddAgent, setShowAddAgent] = useState(false);

  useEffect(() => {
    fetchMembers('current-project-id');
  }, []);

  return (
    <div className="min-h-screen bg-surface">
      <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold font-headline">Team Members</h1>
          <div className="flex gap-4">
            <button
              onClick={() => setShowAddMember(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              + Add Member
            </button>
            <button
              onClick={() => setShowAddAgent(true)}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-colors"
            >
              + Add AI Agent
            </button>
          </div>
        </div>

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

### 5.2 Agent Card Component

```tsx
// app/components/team/AgentCard.tsx
'use client';

import { useState } from 'react';
import AgentMemoryViewer from './AgentMemoryViewer';
import { AIAgent } from '@/stores/teamStore';

interface AgentCardProps {
  agent: AIAgent;
}

export default function AgentCard({ agent }: AgentCardProps) {
  const [showMemory, setShowMemory] = useState(false);

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'analysis_agent':
        return 'bg-amber-100 text-amber-800';
      case 'design_agent':
        return 'bg-blue-100 text-blue-800';
      case 'development_agent':
        return 'bg-emerald-100 text-emerald-800';
      case 'testing_agent':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow group">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-2xl">
            <span className="material-symbols-outlined">smart_toy</span>
          </div>
          <div>
            <h3 className="font-bold text-lg font-headline">{agent.nickname}</h3>
            <p className="text-sm text-gray-600">{agent.name}</p>
          </div>
        </div>
        <span className={`text-xs font-bold px-3 py-1 rounded-full ${getRoleBadgeColor(agent.role)}`}>
          {agent.role.replace('_', ' ').replace(' agent', '').toUpperCase()}
        </span>
      </div>

      <div className="space-y-3 mb-6">
        {agent.skills.length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">Skills</p>
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
          <p className="text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">Memory</p>
          <div className="flex items-center gap-2">
            <span className={`w-3 h-3 rounded-full ${agent.memoryEnabled ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className="text-sm">
              {agent.memoryEnabled ? 'Enabled (Local Document)' : 'Disabled'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center pt-4 border-t">
        <div className="text-xs text-gray-500">
          Joined {new Date(agent.joinedAt).toLocaleDateString()}
        </div>
        <div className="flex gap-2">
          {agent.memoryEnabled && (
            <button
              onClick={() => setShowMemory(true)}
              className="text-sm text-blue-600 hover:underline"
            >
              View Memory
            </button>
          )}
          <button className="p-2 hover:bg-gray-100 rounded">
            <span className="material-symbols-outlined text-lg">settings</span>
          </button>
        </div>
      </div>

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

### 5.3 Add Agent Dialog

```tsx
// app/components/team/AddAgentDialog.tsx
'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

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
      deepagentConfig: {}
    });

    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add AI Agent</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Agent Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="e.g., Analysis Agent"
            />
          </div>

          <div>
            <Label htmlFor="nickname">Nickname</Label>
            <Input
              id="nickname"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              placeholder="e.g., Alex"
            />
          </div>

          <div>
            <Label htmlFor="role">Role</Label>
            <Select value={role} onValueChange={setRole} required>
              <SelectTrigger>
                <SelectValue placeholder="Select role..." />
              </SelectTrigger>
              <SelectContent>
                {availableRoles.map(r => (
                  <SelectItem key={r} value={r}>
                    {r.replace('_', ' ').replace(' agent', '').toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {existingRoles.length === availableRoles.length && (
              <p className="text-sm text-red-500 mt-1">
                All agent roles are already assigned
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="skills">Skills</Label>
            <Input
              id="skills"
              placeholder="Enter skills separated by commas"
              onChange={(e) => setSkills(e.target.value.split(','))}
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
            <Label htmlFor="memory-enabled" className="text-sm">
              Enable Long-term Memory (local document)
            </Label>
          </div>

          <DialogFooter>
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={!role || !name}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            >
              Add AI Agent
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
```

### 5.4 Agent Memory Viewer

```tsx
// app/components/team/AgentMemoryViewer.tsx
'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useTeamStore } from '@/stores/teamStore';
import { AIAgent } from '@/stores/teamStore';

interface AgentMemoryViewerProps {
  agent: AIAgent;
  onClose: () => void;
}

export default function AgentMemoryViewer({ agent, onClose }: AgentMemoryViewerProps) {
  const { getAgentMemory } = useTeamStore();
  const [memory, setMemory] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadMemory();
  }, [agent.id]);

  const loadMemory = async () => {
    setIsLoading(true);
    try {
      const data = await getAgentMemory(agent.id);
      setMemory(data);
    } catch (error) {
      console.error('Failed to load agent memory:', error);
    }
    setIsLoading(false);
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>{agent.nickname} Memory</DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-blue-600 rounded-full border-t-transparent" />
          </div>
        ) : memory ? (
          <div className="bg-gray-50 rounded-lg p-6 max-h-[500px] overflow-y-auto">
            <pre className="text-sm whitespace-pre-wrap">
              {JSON.stringify(memory, null, 2)}
            </pre>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <p>No memory data available</p>
          </div>
        )}

        <DialogFooter>
          <Button onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

## 6. API Client

### 6.1 API Client

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

### 6.2 API Endpoints

```typescript
// lib/api/projects.ts
import { api } from './client';

export const projectsAPI = {
  async listProjects() {
    return await api.get('/api/v1/projects');
  },

  async getProject(projectId: string) {
    return await api.get(`/api/v1/projects/${projectId}`);
  },

  async createProject(data: any) {
    return await api.post('/api/v1/projects', data);
  },

  async updateProject(projectId: string, data: any) {
    return await api.put(`/api/v1/projects/${projectId}`, data);
  },

  async deleteProject(projectId: string) {
    return await api.delete(`/api/v1/projects/${projectId}`);
  }
};
```

```typescript
// lib/api/requirements.ts
import { api } from './client';

export const requirementsAPI = {
  async listRequirements(projectId: string) {
    return await api.get(`/api/v1/projects/${projectId}/requirements`);
  },

  async getRequirement(requirementId: string) {
    return await api.get(`/api/v1/requirements/${requirementId}`);
  },

  async createRequirement(data: any) {
    return await api.post('/api/v1/requirements', data);
  },

  async updateRequirement(requirementId: string, data: any) {
    return await api.put(`/api/v1/requirements/${requirementId}`, data);
  },

  async deleteRequirement(requirementId: string) {
    return await api.delete(`/api/v1/requirements/${requirementId}`);
  },

  async transitionRequirement(requirementId: string, toStatus: string, aiApproved: boolean) {
    return await api.post(`/api/v1/requirements/${requirementId}/transition`, {
      toStatus,
      aiApproved
    });
  }
};
```

```typescript
// lib/api/team.ts
import { api } from './client';

export const teamAPI = {
  async listMembers(projectId: string) {
    return await api.get(`/api/v1/projects/${projectId}/team`);
  },

  async addMember(projectId: string, data: any) {
    return await api.post(`/api/v1/projects/${projectId}/team`, data);
  },

  async updateMember(memberId: string, data: any) {
    return await api.put(`/api/v1/members/${memberId}`, data);
  },

  async deleteMember(memberId: string) {
    return await api.delete(`/api/v1/members/${memberId}`);
  }
};
```

```typescript
// lib/api/agents.ts
import { api } from './client';

export const agentsAPI = {
  async listAgents(projectId: string) {
    return await api.get(`/api/v1/projects/${projectId}/agents`);
  },

  async addAgent(projectId: string, data: any) {
    return await api.post(`/api/v1/projects/${projectId}/agents`, data);
  },

  async updateAgent(agentId: string, data: any) {
    return await api.put(`/api/v1/agents/${agentId}`, data);
  },

  async deleteAgent(agentId: string) {
    return await api.delete(`/api/v1/agents/${agentId}`);
  },

  async getAgentMemory(agentId: string) {
    return await api.get(`/api/v1/agents/${agentId}/memory`);
  },

  async updateAgentMemory(agentId: string, data: any) {
    return await api.put(`/api/v1/agents/${agentId}/memory`, data);
  }
};
```

## 7. Custom Hooks

### 7.1 Agent Hook

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

## 8. Tailwind Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        surface: '#f8f9fa',
        primary: '#0040a1',
        'primary-container': '#0056d2',
        secondary: '#4f5f77',
        error: '#ba1a1a',
        'on-surface': '#191c1d',
        'on-secondary-container': '#54647b',
        'surface-container': '#edeeef',
        'surface-container-low': '#f3f4f5',
        'surface-container-lowest': '#ffffff',
      },
      fontFamily: {
        headline: ['Manrope', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        label: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
```

## 9. Deployment

### 9.1 Build and Run

```bash
# Build for production
npm run build

# Start production server
npm start
```

### 9.2 Environment Variables

Create a `.env.local` file with the following variables:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
```

## 10. Testing

### 10.1 Unit Tests

```typescript
// app/components/kanban/RequirementCard.test.tsx
import { render, screen } from '@testing-library/react';
import RequirementCard from './RequirementCard';

const mockRequirement = {
  id: '1',
  reqNumber: 1001,
  title: 'Test Requirement',
  description: 'This is a test requirement',
  status: 'analysis',
  priority: 'medium',
  larkDocUrl: 'https://feishu.com',
  larkEditable: true,
  returnCount: 0,
  createdAt: new Date(),
  updatedAt: new Date(),
  createdBy: 'user1'
};

describe('RequirementCard', () => {
  it('renders requirement information', () => {
    render(<RequirementCard requirement={mockRequirement} />);
    
    expect(screen.getByText('REQ-1001')).toBeInTheDocument();
    expect(screen.getByText('Test Requirement')).toBeInTheDocument();
    expect(screen.getByText('This is a test requirement')).toBeInTheDocument();
  });

  it('renders Feishu document link', () => {
    render(<RequirementCard requirement={mockRequirement} />);
    
    expect(screen.getByText('Edit in Feishu')).toBeInTheDocument();
    expect(screen.getByRole('link')).toHaveAttribute('href', 'https://feishu.com');
  });
});
```

## 11. Performance Optimization

1. **Code Splitting**: Use React.lazy() for route-based code splitting
2. **Virtual Scrolling**: Implement react-window for large requirement lists
3. **Request Caching**: Add React Query for API caching
4. **Image Optimization**: Use Next.js Image component
5. **CSS Optimization**: Enable Tailwind JIT mode

## 12. Accessibility

- Semantic HTML tags
- ARIA labels and roles
- Keyboard navigation support
- Screen reader friendly
- WCAG 2.1 AA compliance

## Summary

This implementation guide covers all aspects of building the Stratos Management System frontend. By following this guide, you'll create a modern, AI-native requirement management system with:

1. Core layout and navigation
2. Kanban board with drag-and-drop functionality
3. Team management with AI agents and human members
4. AI agent integration with memory viewing
5. Responsive design
6. Accessibility features

The implementation uses Next.js 14, TypeScript, Tailwind CSS, and shadcn/ui to create a professional and performant user interface.
