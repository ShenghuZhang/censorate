'use client';

import { useEffect } from 'react';
import { useRequirementStore } from '@/app/stores/requirementStore';
import KanbanBoardClient from '@/app/components/kanban/KanbanBoardClient';
import Layout from '@/app/components/layout/Layout';

export default function KanbanPage() {
  const { isLoading, fetchRequirements, requirements } = useRequirementStore();

  const projectId = '58d22de7-ddfd-4996-be3d-48e29599604d';

  useEffect(() => {
    fetchRequirements(projectId);
  }, [fetchRequirements]);

  return (
    <Layout>
      <div className="w-full max-w-none overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center items-center py-24">
            <div className="animate-spin w-8 h-8 border-3 border-gray-200 border-t-blue-600 rounded-full" />
          </div>
        ) : (
          <KanbanBoardClient />
        )}
      </div>
    </Layout>
  );
}
