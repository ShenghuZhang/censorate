// frontend/lib/api/automation.ts
import { api } from './client';

export interface AutomationRule {
  id: string;
  name: string;
  description?: string;
  project_id?: string;
  rule_type: string;
  conditions?: Record<string, any>;
  actions?: Record<string, any>;
  schedule?: string;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

export interface AutomationRuleCreate {
  name: string;
  description?: string;
  rule_type?: string;
  conditions?: Record<string, any>;
  actions?: Record<string, any>;
  schedule?: string;
  is_active?: boolean;
  project_id?: string;
}

export interface AutomationRuleUpdate {
  name?: string;
  description?: string;
  rule_type?: string;
  conditions?: Record<string, any>;
  actions?: Record<string, any>;
  schedule?: string;
  is_active?: boolean;
}

export interface AutomationRuleListResponse {
  count: number;
  rules: AutomationRule[];
}

export interface AutomationExecutionResult {
  rule: string;
  success: boolean;
  message?: string;
  results?: Record<string, any>[];
}

export const automationAPI = {
  listRules: (projectId?: string, isActive?: boolean) => {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId);
    if (isActive !== undefined) params.append('is_active', String(isActive));
    const qs = params.toString();
    return api.get<AutomationRuleListResponse>(`/automation/rules${qs ? `?${qs}` : ''}`);
  },
  getRule: (ruleId: string) =>
    api.get<AutomationRule>(`/automation/rules/${ruleId}`),
  createRule: (data: AutomationRuleCreate) =>
    api.post<AutomationRule>('/automation/rules', data),
  updateRule: (ruleId: string, data: AutomationRuleUpdate) =>
    api.put<AutomationRule>(`/automation/rules/${ruleId}`, data),
  deleteRule: (ruleId: string) =>
    api.delete(`/automation/rules/${ruleId}`),
  executeRule: (ruleId: string, eventData: Record<string, any>) =>
    api.post<AutomationExecutionResult>(`/automation/rules/${ruleId}/execute`, { event_data: eventData }),
  executeEvents: (eventType: string, eventData: Record<string, any>, projectId?: string) => {
    const params = projectId ? `?project_id=${projectId}` : '';
    return api.post<{ count: number; results: AutomationExecutionResult[] }>(
      `/automation/events/${eventType}/execute${params}`,
      { event_data: eventData }
    );
  },
  toggleRule: (ruleId: string) =>
    api.post<AutomationRule>(`/automation/rules/${ruleId}/toggle`),
};
