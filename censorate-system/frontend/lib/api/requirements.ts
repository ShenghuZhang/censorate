// frontend/lib/api/requirements.ts
import { api } from './client';

export interface Requirement {
  id: string;
  projectId: string;
  reqNumber: number;
  title: string;
  description?: string;
  status: string;
  priority: 'low' | 'medium' | 'high';
  source?: string;
  assignedTo?: string;
  assignedToName?: string;
  assigned_to_name?: string;
  expectedCompletionAt?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt?: string;
  ai_suggestions?: any;
  returnCount?: number;
}

export interface RequirementStatusHistory {
  id: string;
  requirementId: string;
  fromStatus: string | null;
  toStatus: string;
  changedBy: string;
  changedByName: string;
  note?: string;
  isBackward: boolean;
  changedAt: string;
  assignedTo?: string;
  expectedCompletionAt?: string;
}

export interface Comment {
  id: string;
  requirementId: string;
  content: string;
  authorName: string;
  isAi?: boolean;
  createdAt: string;
  updatedAt?: string;
}

export interface TransitionWithDataRequest {
  toStatus: string;
  note?: string;
  assignedTo?: string;
  assignedToName?: string;
  expectedCompletionAt?: string;
  aiApproved?: boolean;
  changedBy?: string;
  changedByName?: string;
}

export interface CreateCommentRequest {
  content: string;
  authorName?: string;
  authorId?: string;
  isAi?: boolean;
}

export interface CreateRequirementRequest {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  source?: string;
}

export interface UpdateRequirementRequest {
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  assignedTo?: string;
}

export interface TransitionRequest {
  toStatus: string;
  aiApproved?: boolean;
  note?: string;
}

export const requirementsAPI = {
  getRequirements: (projectId: string) =>
    api.get<Requirement[]>(`/projects/${projectId}/requirements`),
  getRequirement: (id: string) =>
    api.get<Requirement>(`/requirements/${id}`),
  createRequirement: (projectId: string, data: CreateRequirementRequest) =>
    api.post<Requirement>(`/projects/${projectId}/requirements`, data),
  updateRequirement: (id: string, data: UpdateRequirementRequest) =>
    api.put<Requirement>(`/requirements/${id}`, data),
  transitionRequirement: (id: string, data: TransitionRequest) =>
    api.post<Requirement>(`/requirements/${id}/transition`, {
      to_status: data.toStatus,
      ai_approved: data.aiApproved ?? false,
      note: data.note,
    }),
  transitionWithData: (id: string, data: TransitionWithDataRequest) =>
    api.post<Requirement>(`/requirements/${id}/transition-with-data`, {
      to_status: data.toStatus,
      assigned_to: data.assignedTo,
      assigned_to_name: data.assignedToName,
      expected_completion_at: data.expectedCompletionAt,
      note: data.note,
      changed_by: data.changedBy,
      changed_by_name: data.changedByName,
      ai_approved: data.aiApproved ?? false,
    }),
  aiAnalyzeRequirement: (id: string) =>
    api.post<any>(`/requirements/${id}/ai-analyze`),
  getHistory: (id: string) =>
    api.get<RequirementStatusHistory[]>(`/requirements/${id}/history`),
  getComments: (id: string) =>
    api.get<Comment[]>(`/requirements/${id}/comments`),
  createComment: (id: string, data: CreateCommentRequest) =>
    api.post<Comment>(`/requirements/${id}/comments`, data),
  uploadAttachment: (id: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8216/api/v1'}/requirements/${id}/attachments`,
      {
        method: 'POST',
        body: formData,
        headers: {
          ...(localStorage.getItem('auth-storage')
            ? { Authorization: `Bearer ${JSON.parse(localStorage.getItem('auth-storage')!).state.token}` }
            : {}),
        },
      }
    ).then(r => r.json());
  },
};
