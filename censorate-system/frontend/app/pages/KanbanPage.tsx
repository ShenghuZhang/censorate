'use client';

import { useEffect } from 'react';
import { useRequirementStore } from '@/app/stores/requirementStore';
import KanbanBoard from '@/app/components/kanban/KanbanBoard';
import Layout from '@/app/components/layout/Layout';

export default function KanbanPage() {
  const { isLoading, fetchRequirements, requirements } = useRequirementStore();

  // Fetch requirements on mount
  // In real app, you would get projectId from context or params
  const projectId = '58d22de7-ddfd-4996-be3d-48e29599604d';

  useEffect(() => {
    fetchRequirements(projectId);
  }, [fetchRequirements]);

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Project Kanban</h1>
            <p className="text-gray-600 mt-2">Manage requirements and track progress</p>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-blue-600 rounded-full border-t-transparent" />
          </div>
        ) : (
          <div>
            <KanbanBoard />
          </div>
        )}
      </div>
    </Layout>
  );
}
