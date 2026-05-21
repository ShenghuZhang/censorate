'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/hooks/useAuth';
import { useGenerationProjectStore } from '@/app/stores/generationProjectStore';
import NewProjectForm from '@/app/components/generation/NewProjectForm';
import Layout from '@/app/components/layout/Layout';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const { projects, fetchProjects, isLoading } = useGenerationProjectStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchProjects();
  }, [isAuthenticated, router, fetchProjects]);

  if (!isAuthenticated) return null;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Hero */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Code Generator</h1>
          <p className="mt-2 text-gray-600">
            Describe your idea and let AI generate a complete, runnable code repository.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* New Project Form */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">New Project</h2>
            <NewProjectForm />
          </div>

          {/* Recent Projects */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Projects</h2>
            {isLoading ? (
              <div className="flex justify-center py-8">
                <div className="w-6 h-6 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
              </div>
            ) : projects.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">
                No projects yet. Describe your idea and generate your first codebase.
              </p>
            ) : (
              <div className="space-y-2">
                {projects.map((project) => (
                  <button
                    key={project.id}
                    onClick={() => router.push(`/projects/${project.id}`)}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors text-left"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{project.name}</p>
                      <p className="text-xs text-gray-500">{new Date(project.created_at).toLocaleDateString()}</p>
                    </div>
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 capitalize">
                      {project.status}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
