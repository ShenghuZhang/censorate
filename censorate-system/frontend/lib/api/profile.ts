// frontend/lib/api/profile.ts
import { api } from './client';

export interface UserProject {
  id: string;
  name: string;
  description?: string;
  role: string;
  created_at: string;
}

export interface UserActivity {
  id: string;
  type: string;
  action: string;
  target: string;
  note?: string;
  timestamp: string;
}

export interface ContributionDay {
  date: string;
  count: number;
}

export interface ContributionHeatmap {
  total: number;
  contributions: ContributionDay[];
}

export const profileAPI = {
  getUserProjects: (userId: string) =>
    api.get<UserProject[]>(`/users/${userId}/projects`),
  getUserActivity: (userId: string) =>
    api.get<UserActivity[]>(`/users/${userId}/activity`),
  getUserHeatmap: (userId: string) =>
    api.get<ContributionHeatmap>(`/users/${userId}/heatmap`),
  updateProfile: (userId: string, data: any) =>
    api.put<any>(`/users/${userId}`, data),
};
