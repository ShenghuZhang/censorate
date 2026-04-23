'use client';

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { projectsAPI, type Project, type ProjectCreate, type ProjectUpdate } from '@/lib/api/projects';

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  error: string | null;

  fetchProjects: () => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: ProjectCreate) => Promise<Project | null>;
  updateProject: (id: string, data: ProjectUpdate) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  setCurrentProject: (project: Project | null) => void;
  clearError: () => void;
}

export const useProjectStore = create<ProjectState>()(
  devtools(
    (set, get) => ({
      projects: [],
      currentProject: null,
      isLoading: false,
      error: null,

      fetchProjects: async () => {
        set({ isLoading: true, error: null });
        try {
          const projects = await projectsAPI.getProjects();
          set({ projects, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch projects',
            isLoading: false
          });
        }
      },

      fetchProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const project = await projectsAPI.getProject(id);
          set({ currentProject: project, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch project',
            isLoading: false
          });
        }
      },

      createProject: async (data: ProjectCreate) => {
        set({ isLoading: true, error: null });
        try {
          const newProject = await projectsAPI.createProject(data);
          set((state) => ({
            projects: [...state.projects, newProject],
            isLoading: false
          }));
          return newProject;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create project',
            isLoading: false
          });
          return null;
        }
      },

      updateProject: async (id: string, data: ProjectUpdate) => {
        set({ isLoading: true, error: null });
        try {
          const updatedProject = await projectsAPI.updateProject(id, data);
          set((state) => ({
            projects: state.projects.map(p => p.id === id ? updatedProject : p),
            currentProject: state.currentProject?.id === id ? updatedProject : state.currentProject,
            isLoading: false
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update project',
            isLoading: false
          });
        }
      },

      deleteProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await projectsAPI.deleteProject(id);
          set((state) => ({
            projects: state.projects.filter(p => p.id !== id),
            currentProject: state.currentProject?.id === id ? null : state.currentProject,
            isLoading: false
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to delete project',
            isLoading: false
          });
        }
      },

      setCurrentProject: (project: Project | null) => {
        set({ currentProject: project });
      },

      clearError: () => {
        set({ error: null });
      }
    })
  )
);
