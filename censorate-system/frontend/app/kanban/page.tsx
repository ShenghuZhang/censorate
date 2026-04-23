'use client';

import { useEffect } from 'react';
import { useRequirementStore } from '@/app/stores/requirementStore';
import { useProjectStore } from '@/app/stores/projectStore';
import { useRouter, useSearchParams } from 'next/navigation';
import KanbanBoardClient from '@/app/components/kanban/KanbanBoardClient';
import Layout from '@/app/components/layout/Layout';

export default function KanbanPage() {
  const { isLoading: isLoadingRequirements, fetchRequirements } = useRequirementStore();
  const { currentProject, fetchProject, isLoading: isLoadingProject, projects, fetchProjects, setCurrentProject } = useProjectStore();
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams?.get('project_id');

  // Fetch projects if not already loaded
  useEffect(() => {
    if (projects.length === 0) {
      fetchProjects();
    }
  }, [projects.length, fetchProjects]);

  // Handle project_id from URL
  useEffect(() => {
    if (projectId) {
      // If URL has project_id, fetch and set as current project
      if (!currentProject || currentProject.id !== projectId) {
        fetchProject(projectId);
      }
    } else if (currentProject) {
      // No project_id in URL but we have currentProject, update URL
      router.replace(`/kanban?project_id=${currentProject.id}`);
    } else if (projects.length > 0) {
      // No project_id and no currentProject, use first project
      const firstProject = projects[0];
      setCurrentProject(firstProject);
      router.replace(`/kanban?project_id=${firstProject.id}`);
    }
  }, [projectId, currentProject, projects, fetchProject, setCurrentProject, router]);

  // Redirect to projects if no projects and no project_id
  useEffect(() => {
    if (!projectId && projects.length === 0 && !isLoadingProject) {
      router.push('/projects');
    }
  }, [projectId, projects.length, isLoadingProject, router]);

  // Fetch requirements when we have a current project
  useEffect(() => {
    if (currentProject) {
      fetchRequirements(currentProject.id);
    }
  }, [currentProject, fetchRequirements]);

  if (!currentProject) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-24">
          <div className="animate-spin w-8 h-8 border-3 border-border border-t-primary rounded-full" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="w-full max-w-none overflow-hidden">
        {isLoadingRequirements || isLoadingProject ? (
          <div className="flex justify-center items-center py-24">
            <div className="animate-spin w-8 h-8 border-3 border-border border-t-primary rounded-full" />
          </div>
        ) : (
          <KanbanBoardClient />
        )}
      </div>
    </Layout>
  );
}
