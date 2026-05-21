import { api } from './client';

export interface Template {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  tech_stack: Record<string, any>;
  is_monorepo: boolean;
  config: Record<string, any>;
  is_active: boolean;
  created_at: string;
}

export const templatesAPI = {
  list: () => api.get<Template[]>('/templates/'),
  get: (id: string) => api.get<Template>(`/templates/${id}`),
};
