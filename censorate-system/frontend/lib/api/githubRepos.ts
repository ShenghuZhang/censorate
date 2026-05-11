// frontend/lib/api/githubRepos.ts
import { api } from './client';

export interface GitHubRepo {
  id: string;
  project_id: string;
  url: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export const githubReposAPI = {
  listRepos: (projectId: string) =>
    api.get<GitHubRepo[]>(`/projects/${projectId}/github-repos`),
  addRepo: (projectId: string, data: { url: string, description?: string }) =>
    api.post<GitHubRepo>(`/projects/${projectId}/github-repos`, data),
  deleteRepo: (projectId: string, repoId: string) =>
    api.delete(`/projects/${projectId}/github-repos/${repoId}`),
};
