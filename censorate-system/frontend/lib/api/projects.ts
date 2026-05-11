// frontend/lib/api/projects.ts
import { api } from './client';

export interface Project {
  id: string;
  name: string;
  slug: string;
  description?: string;
  project_type: string;
  projectType: string;
  settings: {
    swimlanes?: string[];
    emoji?: string;
    [key: string]: any;
  };
  created_by?: string;
  createdBy?: string;
  created_at: string;
  createdAt: string;
  updated_at?: string;
  updatedAt?: string;
  archived_at?: string | null;
  archivedAt?: string | null;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  project_type: string;
  settings?: any;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  settings?: any;
}

export const projectsAPI = {
  getProjects: () => api.get<Project[]>('/projects'),
  getProject: (id: string) => api.get<Project>(`/projects/${id}`),
  createProject: (data: ProjectCreate) => api.post<Project>('/projects', data),
  updateProject: (id: string, data: ProjectUpdate) => api.put<Project>(`/projects/${id}`, data),
  deleteProject: (id: string) => api.delete(`/projects/${id}`),
};
