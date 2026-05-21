'use client';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  generationProjectsAPI,
  type GenerationProject,
  type GenerationProjectDetail,
  type ProjectCreate,
  type PRDConfirmation,
  type CodeApproval,
} from '@/lib/api/generation-projects';

interface GenerationProjectState {
  projects: GenerationProject[];
  currentProject: GenerationProjectDetail | null;
  isLoading: boolean;
  error: string | null;

  fetchProjects: () => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: ProjectCreate) => Promise<GenerationProject | null>;
  confirmPRD: (id: string, data: PRDConfirmation) => Promise<void>;
  approveArchitecture: (id: string) => Promise<void>;
  approveCode: (id: string, data: CodeApproval) => Promise<void>;
  retryProject: (id: string) => Promise<void>;
  cancelProject: (id: string) => Promise<void>;
  setCurrentProject: (project: GenerationProjectDetail | null) => void;
  clearError: () => void;
}

export const useGenerationProjectStore = create<GenerationProjectState>()(
  devtools(
    (set, get) => ({
      projects: [],
      currentProject: null,
      isLoading: false,
      error: null,

      fetchProjects: async () => {
        set({ isLoading: true, error: null });
        try {
          const projects = await generationProjectsAPI.list();
          set({ projects, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch projects',
            isLoading: false,
          });
        }
      },

      fetchProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const project = await generationProjectsAPI.get(id);
          set({ currentProject: project, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch project',
            isLoading: false,
          });
        }
      },

      createProject: async (data: ProjectCreate) => {
        set({ isLoading: true, error: null });
        try {
          const project = await generationProjectsAPI.create(data);
          set((state) => ({
            projects: [project, ...state.projects],
            isLoading: false,
          }));
          return project;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create project',
            isLoading: false,
          });
          return null;
        }
      },

      confirmPRD: async (id: string, data: PRDConfirmation) => {
        set({ isLoading: true, error: null });
        try {
          const project = await generationProjectsAPI.confirm(id, data);
          set({ currentProject: project, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to confirm PRD',
            isLoading: false,
          });
        }
      },

      approveArchitecture: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const project = await generationProjectsAPI.approveArchitecture(id);
          set({ currentProject: project, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to approve architecture',
            isLoading: false,
          });
        }
      },

      approveCode: async (id: string, data: CodeApproval) => {
        set({ isLoading: true, error: null });
        try {
          const project = await generationProjectsAPI.approveCode(id, data);
          set({ currentProject: project, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to approve code',
            isLoading: false,
          });
        }
      },

      retryProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const project = await generationProjectsAPI.retry(id);
          set({ currentProject: project, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to retry project',
            isLoading: false,
          });
        }
      },

      cancelProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const project = await generationProjectsAPI.cancel(id);
          set({ currentProject: project, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to cancel project',
            isLoading: false,
          });
        }
      },

      setCurrentProject: (project) => {
        set({ currentProject: project });
      },

      clearError: () => {
        set({ error: null });
      },
    })
  )
);
