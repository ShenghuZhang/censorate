import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type RequirementStatus = 'backlog' | 'todo' | 'in_review' | 'done';
export type Priority = 'low' | 'medium' | 'high';

export interface Requirement {
  id: string;
  projectId: string;
  reqNumber: number;
  title: string;
  description?: string;
  status: RequirementStatus;
  priority: Priority;
  source?: string;
  sourceMetadata?: any;

  larkDocToken?: string;
  larkDocUrl?: string;
  larkEditable: boolean;

  aiSuggestions?: any;
  currentAgent?: string;
  aiConfidence?: number;

  returnCount: number;
  lastReturnedAt?: Date;

  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  assignedTo?: string;
}

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

// Generate demo data for analytics
const generateDemoData = (): Requirement[] => {
  const members = ['user-1', 'user-2', 'user-3', 'user-4'];
  const statuses: RequirementStatus[] = ['backlog', 'todo', 'in_review', 'done'];
  const priorities: Priority[] = ['low', 'medium', 'high'];
  const titles = [
    'Design user authentication flow',
    'Implement REST API endpoints',
    'Create database schema',
    'Write unit tests for services',
    'Design responsive UI components',
    'Optimize database queries',
    'Add error handling middleware',
    'Implement real-time notifications',
    'Create project setup wizard',
    'Design analytics dashboard',
    'Implement file upload feature',
    'Add search functionality',
    'Create export to PDF feature',
    'Implement role-based access control',
    'Add audit logging system',
    'Refactor service layer',
    'Update API documentation',
    'Add data validation',
    'Implement caching strategy',
    'Design mobile app UI',
    'Add rate limiting',
    'Implement webhook integration',
    'Create email templates',
    'Add scheduled jobs',
    'Implement two-factor auth',
  ];

  const data: Requirement[] = [];
  const now = new Date();

  for (let i = 0; i < 25; i++) {
    const createdAt = new Date(now);
    createdAt.setDate(createdAt.getDate() - Math.floor(Math.random() * 14));
    const updatedAt = new Date(createdAt);
    updatedAt.setDate(updatedAt.getDate() + Math.floor(Math.random() * 7));

    const status = statuses[Math.floor(Math.random() * statuses.length)];

    data.push({
      id: `req-${i + 1}`,
      projectId: 'demo-project',
      reqNumber: i + 1,
      title: titles[i % titles.length],
      description: `This is a sample requirement for ${titles[i % titles.length]}`,
      status,
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      source: 'manual',
      larkEditable: false,
      returnCount: Math.random() > 0.8 ? Math.floor(Math.random() * 3) : 0,
      createdAt,
      updatedAt: status === 'done' ? updatedAt : new Date(),
      createdBy: members[Math.floor(Math.random() * members.length)],
      assignedTo: members[Math.floor(Math.random() * members.length)],
    });
  }

  return data;
};

const demoRequirements: Requirement[] = generateDemoData();

export const useRequirementStore = create<RequirementState>()(
  devtools(
    (set, get) => ({
      requirements: demoRequirements,
      selectedRequirement: null,
      isLoading: false,
      error: null,

      fetchRequirements: async (projectId: string) => {
        set({ isLoading: true });
        try {
          // Demo mode - use local data
          await new Promise(resolve => setTimeout(resolve, 300));
          set({ requirements: demoRequirements, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to fetch requirements', isLoading: false });
        }
      },

      createRequirement: async (projectId: string, data: Partial<Requirement>) => {
        set({ isLoading: true });
        try {
          // Demo mode - add to local array
          const newReq: Requirement = {
            id: 'req-' + Date.now(),
            projectId: projectId,
            reqNumber: get().requirements.length + 1,
            title: data.title || 'New requirement',
            description: data.description,
            status: 'backlog',
            priority: data.priority || 'medium',
            source: data.source || 'manual',
            larkEditable: false,
            returnCount: 0,
            createdAt: new Date(),
            updatedAt: new Date(),
            createdBy: 'demo-user'
          };

          set((state) => ({
            requirements: [...state.requirements, newReq],
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to create requirement', isLoading: false });
        }
      },

      updateRequirement: async (id: string, updates: Partial<Requirement>) => {
        set({ isLoading: true });
        try {
          // Demo mode - update local array
          set((state) => ({
            requirements: state.requirements.map(req =>
              req.id === id ? { ...req, ...updates, updatedAt: new Date() } : req
            ),
            selectedRequirement: state.selectedRequirement?.id === id
              ? { ...state.selectedRequirement, ...updates, updatedAt: new Date() }
              : state.selectedRequirement,
            isLoading: false
          }));
        } catch (error) {
          set({ error: 'Failed to update requirement', isLoading: false });
        }
      },

      transitionRequirement: async (id: string, toStatus: string, aiApproved: boolean) => {
        try {
          // Demo mode - update status locally
          set((state) => {
            const updatedRequirements = state.requirements.map(req => {
              if (req.id === id) {
                const updated = {
                  ...req,
                  status: toStatus as RequirementStatus,
                  updatedAt: new Date()
                };
                // Track backward transitions
                const statusOrder: RequirementStatus[] = ['backlog', 'todo', 'in_review', 'done'];
                const fromIndex = statusOrder.indexOf(req.status);
                const toIndex = statusOrder.indexOf(toStatus as RequirementStatus);
                if (toIndex < fromIndex) {
                  updated.returnCount = req.returnCount + 1;
                }
                return updated;
              }
              return req;
            });

            return {
              requirements: updatedRequirements,
              selectedRequirement: updatedRequirements.find(r => r.id === id) || null
            };
          });
        } catch (error) {
          console.error('Failed to transition requirement:', error);
        }
      },

      aiAnalyzeRequirement: async (id: string) => {
        try {
          // Demo mode - no-op
          await new Promise(resolve => setTimeout(resolve, 500));
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
