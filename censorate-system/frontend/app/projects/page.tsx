'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Plus,
  Search,
  MoreVertical,
  FolderKanban,
  Calendar,
  Pencil,
  Trash2
} from 'lucide-react';
import { useProjectStore } from '@/app/stores/projectStore';
import { useAuth } from '@/app/hooks/useAuth';
import Layout from '@/app/components/layout/Layout';
import CreateProjectDialog from '@/app/components/projects/CreateProjectDialog';

export default function ProjectsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const { projects, isLoading, error, fetchProjects, createProject, updateProject, deleteProject, setCurrentProject } = useProjectStore();
  const [showDialog, setShowDialog] = useState(false);
  const [editProject, setEditProject] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchProjects();
  }, [isAuthenticated, router, fetchProjects]);

  const handleCreateProject = async (data: any) => {
    if (editProject) {
      await updateProject(editProject.id, data);
      setShowDialog(false);
      setEditProject(null);
    } else {
      const newProject = await createProject(data);
      if (newProject) {
        setShowDialog(false);
        setCurrentProject(newProject);
        router.push(`/kanban?project_id=${newProject.id}`);
      }
    }
  };

  const handleEditProject = (project: any) => {
    setEditProject(project);
    setShowDialog(true);
  };

  const handleDeleteProject = async (projectId: string) => {
    if (confirm('Are you sure you want to delete this project?')) {
      await deleteProject(projectId);
    }
  };

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!isAuthenticated) return null;

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-text-primary tracking-tight">Projects</h1>
            <p className="text-text-tertiary mt-1.5">Manage your projects and requirements</p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search projects..."
                className="pl-12 pr-4 py-2.5 w-full sm:w-72 bg-surface border border-border rounded-xl focus:ring-2 focus:ring-ring focus:border-border-medium outline-none transition-all text-sm shadow-soft"
              />
            </div>

            <button
              onClick={() => setShowDialog(true)}
              className="flex items-center justify-center gap-2 px-5 py-2.5 bg-primary text-white rounded-xl hover:bg-primary-dark transition-all font-medium text-sm shadow-soft shadow-primary/25"
            >
              <Plus className="w-5 h-5" />
              New Project
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-error-soft border border-red-200/80 rounded-xl">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="w-10 h-10 border-3 border-border border-t-primary rounded-full animate-spin mb-4" />
            <p className="text-text-tertiary font-medium">Loading projects...</p>
          </div>
        ) : (
          <>
            {filteredProjects.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-center bg-surface rounded-2xl border border-border shadow-soft">
                <div className="w-24 h-24 bg-surface-soft rounded-3xl flex items-center justify-center mb-6">
                  <FolderKanban className="w-12 h-12 text-text-muted" />
                </div>
                <h3 className="text-xl font-semibold text-text-primary mb-2 tracking-tight">
                  {searchQuery ? 'No projects found' : 'No projects yet'}
                </h3>
                <p className="text-text-tertiary mb-8 max-w-md">
                  {searchQuery
                    ? 'Try adjusting your search query'
                    : 'Create your first project to get started with requirement management'
                  }
                </p>
                {!searchQuery && (
                  <button
                    onClick={() => setShowDialog(true)}
                    className="flex items-center gap-2 px-5 py-2.5 bg-primary text-white rounded-xl hover:bg-primary-dark transition-all font-medium text-sm shadow-soft shadow-primary/25"
                  >
                    <Plus className="w-5 h-5" />
                    Create First Project
                  </button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredProjects.map((project, index) => (
                  <div
                    key={project.id}
                    className="group bg-surface rounded-2xl shadow-soft hover:shadow-elevated hover:-translate-y-1 transition-all border border-border overflow-hidden animate-fade-in-up"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="h-2 bg-gradient-to-r from-primary to-primary-dark" />

                    <div className="p-6">
                      <div className="flex justify-between items-start mb-5">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-xl bg-surface-soft flex items-center justify-center text-3xl">
                            {project.settings?.emoji || <FolderKanban className="w-6 h-6 text-text-muted" />}
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleEditProject(project)}
                            className="p-2 text-text-muted hover:text-text-secondary hover:bg-surface-soft rounded-xl transition-colors"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteProject(project.id)}
                            className="p-2 text-text-muted hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      <h3 className="text-lg font-semibold text-text-primary mb-3 group-hover:text-primary transition-colors tracking-tight">
                        {project.name}
                      </h3>

                      {project.description && (
                        <p className="text-text-tertiary text-sm mb-6 line-clamp-2 leading-relaxed">
                          {project.description}
                        </p>
                      )}

                      <div className="flex items-center gap-4 text-sm text-text-muted mb-6">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-4 h-4" />
                          <span>
                            {new Date(project.createdAt).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      <button
                        onClick={() => {
                          setCurrentProject(project);
                          router.push(`/kanban?project_id=${project.id}`);
                        }}
                        className="w-full py-3 text-sm font-medium text-text-secondary bg-surface-soft hover:bg-surface-softer rounded-xl transition-colors"
                      >
                        Open Project
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

      <CreateProjectDialog
        isOpen={showDialog}
        onClose={() => {
          setShowDialog(false);
          setEditProject(null);
        }}
        onSubmit={handleCreateProject}
        isLoading={isLoading}
        editProject={editProject}
      />
      </div>
    </Layout>
  );
}
