'use client';

import Layout from '@/app/components/layout/Layout';
import StatusOverview from '@/app/components/analytics/StatusOverview';
import ThroughputChart from '@/app/components/analytics/ThroughputChart';
import WorkloadChart from '@/app/components/analytics/WorkloadChart';
import { useProjectStore } from '@/app/stores/projectStore';
import { useAnalytics } from '@/app/hooks/useAnalytics';
import { BarChart3, Loader2, AlertCircle } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

export default function AnalyticsPage() {
  const { currentProject, fetchProject, projects, fetchProjects, setCurrentProject, isLoading: isLoadingProject } = useProjectStore();
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams?.get('project_id');

  const { statusStats, dailyThroughput, memberWorkload, totalRequirements, isLoading, error, refetch } = useAnalytics(
    currentProject?.id || null
  );

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
      router.replace(`/analytics?project_id=${currentProject.id}`);
    } else if (projects.length > 0) {
      // No project_id and no currentProject, use first project
      const firstProject = projects[0];
      setCurrentProject(firstProject);
      router.replace(`/analytics?project_id=${firstProject.id}`);
    }
  }, [projectId, currentProject, projects, fetchProject, setCurrentProject, router]);

  if (isLoading || isLoadingProject) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-[#1f2328] flex items-center gap-3">
                <BarChart3 size={28} className="text-[#0969da]" />
                Analytics
              </h1>
            </div>
          </div>
          <div className="flex items-center justify-center h-64">
            <Loader2 size={40} className="text-[#0969da] animate-spin" />
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-[#1f2328] flex items-center gap-3">
                <BarChart3 size={28} className="text-[#0969da]" />
                Analytics
              </h1>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-[#d0d7de] p-12 text-center">
            <div className="w-16 h-16 bg-[#ffebe9] rounded-2xl flex items-center justify-center mx-auto mb-4">
              <AlertCircle size={32} className="text-[#cf222e]" />
            </div>
            <h3 className="text-lg font-semibold text-[#1f2328] mb-2">
              Failed to Load Analytics
            </h3>
            <p className="text-[#656d76] mb-4">{error}</p>
            <button
              onClick={refetch}
              className="px-4 py-2 bg-[#0969da] text-white rounded-lg hover:bg-[#218bff] transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-[#1f2328] flex items-center gap-3">
              <BarChart3 size={28} className="text-[#0969da]" />
              Analytics
            </h1>
            <p className="text-[#656d76] mt-2">
              View project analytics and insights
              {currentProject && (
                <span className="text-[#8193b2] ml-2">
                  for {currentProject.name}
                </span>
              )}
            </p>
          </div>
        </div>

        {currentProject ? (
          <>
            <StatusOverview stats={statusStats} total={totalRequirements} />
            <ThroughputChart data={dailyThroughput} />
            <WorkloadChart data={memberWorkload} />
          </>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-[#d0d7de] p-12 text-center">
            <div className="w-16 h-16 bg-[#f6f8fa] rounded-2xl flex items-center justify-center mx-auto mb-4">
              <BarChart3 size={32} className="text-[#656d76]" />
            </div>
            <h3 className="text-lg font-semibold text-[#1f2328] mb-2">
              Select a Project
            </h3>
            <p className="text-[#656d76]">
              Choose a project from the header to view analytics
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
