import { api } from './client';

export interface GenerationProject {
  id: string;
  name: string;
  description: string | null;
  status: string;
  template_id: string;
  repo_url: string | null;
  created_at: string;
  error_message: string | null;
}

export interface GenerationProjectDetail extends GenerationProject {
  prd_content: Record<string, any> | null;
  architecture_design: Record<string, any> | null;
  steps: PipelineStep[];
  files: GeneratedFile[];
}

export interface PipelineStep {
  id: string;
  step_type: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
  retry_count: number;
}

export interface GeneratedFile {
  id: string;
  file_path: string;
  language: string | null;
  step: string;
  status: string;
}

export interface GeneratedFileDetail extends GeneratedFile {
  content: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  user_story: string;
  template_slug: string;
}

export interface PRDConfirmation {
  confirmed: boolean;
  edited_prd?: Record<string, any>;
  feedback?: string;
}

export interface CodeApproval {
  approved: boolean;
  feedback?: string;
}

export const generationProjectsAPI = {
  list: () => api.get<GenerationProject[]>('/generation-projects/'),
  create: (data: ProjectCreate) => api.post<GenerationProject>('/generation-projects/', data),
  get: (id: string) => api.get<GenerationProjectDetail>(`/generation-projects/${id}`),
  confirm: (id: string, data: PRDConfirmation) =>
    api.post<GenerationProjectDetail>(`/generation-projects/${id}/confirm`, data),
  approveArchitecture: (id: string) =>
    api.post<GenerationProjectDetail>(`/generation-projects/${id}/approve-architecture`),
  approveCode: (id: string, data: CodeApproval) =>
    api.post<GenerationProjectDetail>(`/generation-projects/${id}/approve-code`, data),
  retry: (id: string) =>
    api.post<GenerationProjectDetail>(`/generation-projects/${id}/retry`),
  cancel: (id: string) =>
    api.post<GenerationProjectDetail>(`/generation-projects/${id}/cancel`),
};
