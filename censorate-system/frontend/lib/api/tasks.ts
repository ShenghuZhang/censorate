// frontend/lib/api/tasks.ts
import { api } from './client';

export interface Task {
  id: string;
  requirement_id: string;
  task_number: number;
  title: string;
  description?: string;
  status: string;
  estimate_hours?: number;
  github_pr_url?: string;
  created_by: string;
  assigned_to?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  estimate_hours?: number;
  assigned_to?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: string;
  estimate_hours?: number;
  github_pr_url?: string;
  assigned_to?: string;
  started_at?: string;
  completed_at?: string;
}

export const tasksAPI = {
  listTasks: (requirementId: string) =>
    api.get<Task[]>(`/requirements/${requirementId}/tasks`),
  getTask: (taskId: string) =>
    api.get<Task>(`/tasks/${taskId}`),
  createTask: (requirementId: string, data: TaskCreate) =>
    api.post<Task>(`/requirements/${requirementId}/tasks`, data),
  updateTask: (taskId: string, data: TaskUpdate) =>
    api.put<Task>(`/tasks/${taskId}`, data),
  deleteTask: (taskId: string) =>
    api.delete(`/tasks/${taskId}`),
  generateTests: (taskId: string) =>
    api.post<{ message: string; task_id: string }>(`/tasks/${taskId}/generate-tests`),
};
