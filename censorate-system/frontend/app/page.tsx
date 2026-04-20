'use client';

import { useEffect } from 'react';
import { useAuth } from './hooks/useAuth';
import { useProjectStore } from './stores/projectStore';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const { projects, currentProject, fetchProjects } = useProjectStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchProjects();
  }, [isAuthenticated, router, fetchProjects]);

  useEffect(() => {
    if (isAuthenticated && projects.length > 0) {
      if (currentProject) {
        router.push('/kanban');
      } else {
        router.push('/projects');
      }
    } else if (isAuthenticated) {
      router.push('/projects');
    }
  }, [isAuthenticated, projects, currentProject, router]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-3 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
        <p className="text-sm text-gray-400">Redirecting...</p>
      </div>
    </div>
  );
}
