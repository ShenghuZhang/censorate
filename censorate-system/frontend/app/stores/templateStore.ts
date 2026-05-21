'use client';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { templatesAPI, type Template } from '@/lib/api/templates';

interface TemplateState {
  templates: Template[];
  isLoading: boolean;
  error: string | null;
  fetchTemplates: () => Promise<void>;
}

export const useTemplateStore = create<TemplateState>()(
  devtools(
    (set) => ({
      templates: [],
      isLoading: false,
      error: null,

      fetchTemplates: async () => {
        set({ isLoading: true, error: null });
        try {
          const templates = await templatesAPI.list();
          set({ templates, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch templates',
            isLoading: false,
          });
        }
      },
    })
  )
);
