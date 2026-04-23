import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { requirementsAPI, type Requirement } from '@/lib/api/requirements';

export type RequirementStatus = string;
export type Priority = 'low' | 'medium' | 'high';

interface RequirementState {
  requirements: Requirement[];
  selectedRequirement: Requirement | null;
  isLoading: boolean;
  error: string | null;
  fetchRequirements: (projectId: string) => Promise<void>;
  createRequirement: (projectId: string, data: Partial<Requirement>) => Promise<void>;
  updateRequirement: (id: string, updates: Partial<Requirement>) => Promise<void>;
  transitionRequirement: (id: string, toStatus: string, aiApproved: boolean) => Promise<void>;
  aiAnalyzeRequirement: (id: string) => Promise<void>;
  getRequirementsByStatus: (status: RequirementStatus) => Requirement[];
  setSelectedRequirement: (requirement: Requirement | null) => void;
}

export const useRequirementStore = create<RequirementState>()(
  devtools(
    (set, get) => ({
      requirements: [],
      selectedRequirement: null,
      isLoading: false,
      error: null,

      fetchRequirements: async (projectId: string) => {
        set({ isLoading: true, error: null });
        try {
          const data = await requirementsAPI.getRequirements(projectId);
          set({ requirements: data, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch requirements',
            isLoading: false
          });
        }
      },

      createRequirement: async (projectId: string, data: Partial<Requirement>) => {
        set({ isLoading: true });
        try {
          const newReq = await requirementsAPI.createRequirement(projectId, {
            title: data.title || 'New requirement',
            description: data.description,
            priority: data.priority || 'medium',
            source: data.source || 'manual'
          });
          set((state) => ({
            requirements: [...state.requirements, newReq],
            isLoading: false
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create requirement',
            isLoading: false
          });
        }
      },

      updateRequirement: async (id: string, updates: Partial<Requirement>) => {
        set({ isLoading: true });
        try {
          const updated = await requirementsAPI.updateRequirement(id, {
            title: updates.title,
            description: updates.description,
            priority: updates.priority,
            assignedTo: updates.assignedTo
          });
          set((state) => ({
            requirements: state.requirements.map(req => req.id === id ? updated : req),
            selectedRequirement: state.selectedRequirement?.id === id ? updated : state.selectedRequirement,
            isLoading: false
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update requirement',
            isLoading: false
          });
        }
      },

      transitionRequirement: async (id: string, toStatus: string, aiApproved: boolean) => {
        try {
          const updated = await requirementsAPI.transitionRequirement(id, {
            toStatus: toStatus as any,
            aiApproved
          });
          set((state) => {
            const updatedRequirements = state.requirements.map(req => req.id === id ? updated : req);
            return {
              requirements: updatedRequirements,
              selectedRequirement: updatedRequirements.find(r => r.id === id) || null
            };
          });
        } catch (error) {
          console.error('Failed to transition requirement:', error);
          throw error;
        }
      },

      aiAnalyzeRequirement: async (id: string) => {
        try {
          await requirementsAPI.aiAnalyzeRequirement(id);
        } catch (error) {
          console.error('Failed to analyze requirement:', error);
        }
      },

      getRequirementsByStatus: (status: RequirementStatus) => {
        return get().requirements.filter(req => req.status === status);
      },

      setSelectedRequirement: (requirement: Requirement | null) => {
        set({ selectedRequirement: requirement });
      }
    })
  )
);
