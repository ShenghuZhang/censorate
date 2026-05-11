// frontend/lib/api/testCases.ts
import { api } from './client';

export interface TestCase {
  id: string;
  requirement_id: string;
  test_number: number;
  title: string;
  description?: string;
  type: string;
  status: string;
  github_run_url?: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
  archived_at?: string;
}

export interface TestCaseCreate {
  title: string;
  description?: string;
  type?: string;
  status?: string;
  github_run_url?: string;
}

export interface TestCaseUpdate {
  title?: string;
  description?: string;
  type?: string;
  status?: string;
  github_run_url?: string;
}

export const testCasesAPI = {
  listTestCases: (requirementId: string) =>
    api.get<TestCase[]>(`/requirements/${requirementId}/test-cases`),
  getTestCase: (testCaseId: string) =>
    api.get<TestCase>(`/test-cases/${testCaseId}`),
  createTestCase: (requirementId: string, data: TestCaseCreate) =>
    api.post<TestCase>(`/requirements/${requirementId}/test-cases`, data),
  updateTestCase: (testCaseId: string, data: TestCaseUpdate) =>
    api.put<TestCase>(`/test-cases/${testCaseId}`, data),
  deleteTestCase: (testCaseId: string) =>
    api.delete(`/test-cases/${testCaseId}`),
};
