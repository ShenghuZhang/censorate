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
  Trash2,
  Users
} from 'lucide-react';
import { useProjectStore } from '@/app/stores/projectStore';
import { useAuth } from '@/app/hooks/useAuth';
import { clsx } from 'clsx';

interface CreateProjectDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  isLoading: boolean;
  editProject?: any;
}

function CreateProjectDialog({ isOpen, onClose, onSubmit, isLoading, editProject }: CreateProjectDialogProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [projectType, setProjectType] = useState<'non_technical' | 'technical'>('non_technical');

  useEffect(() => {
    if (editProject) {
      setName(editProject.name);
      setDescription(editProject.description || '');
      setProjectType(editProject.project_type as 'non_technical' | 'technical');
    } else {
      setName('');
      setDescription('');
      setProjectType('non_technical');
    }
  }, [editProject]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({ name, description, project_type: projectType });
    setName('');
    setDescription('');
    setProjectType('non_technical');
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white/95 backdrop-blur-xl rounded-lg shadow-2xl max-w-md w-full mx-4 p-8 border border-white/60">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">
            {editProject ? 'Edit Project' : 'New Project'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Project Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2.5 bg-gray-50/80 border border-gray-200/80 rounded-lg focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none transition-all text-sm"
              placeholder="Enter project name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2.5 bg-gray-50/80 border border-gray-200/80 rounded-lg focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none transition-all text-sm resize-none"
              rows={3}
              placeholder="Enter project description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Type
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setProjectType('non_technical')}
                className={clsx(
                  "flex items-center gap-3 p-4 rounded-lg border-2 transition-all text-left",
                  projectType === 'non_technical'
                    ? "border-blue-500 bg-blue-50/80"
                    : "border-gray-200 bg-gray-50/50 hover:border-gray-300"
                )}
              >
                <div className={clsx(
                  "w-10 h-10 rounded-lg flex items-center justify-center",
                  projectType === 'non_technical'
                    ? "bg-gradient-to-br from-amber-400 to-orange-500 text-white"
                    : "bg-gray-200 text-gray-500"
                )}>
                  <Users className="w-5 h-5" />
                </div>
                <div>
                  <div className={clsx(
                    "font-medium text-sm",
                    projectType === 'non_technical' ? "text-gray-900" : "text-gray-600"
                  )}>
                    Business
                  </div>
                  <div className="text-xs text-gray-400">
                    Non-technical
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setProjectType('technical')}
                className={clsx(
                  "flex items-center gap-3 p-4 rounded-lg border-2 transition-all text-left",
                  projectType === 'technical'
                    ? "border-blue-500 bg-blue-50/80"
                    : "border-gray-200 bg-gray-50/50 hover:border-gray-300"
                )}
              >
                <div className={clsx(
                  "w-10 h-10 rounded-lg flex items-center justify-center",
                  projectType === 'technical'
                    ? "bg-gradient-to-br from-purple-500 to-indigo-600 text-white"
                    : "bg-gray-200 text-gray-500"
                )}>
                  <FolderKanban className="w-5 h-5" />
                </div>
                <div>
                  <div className={clsx(
                    "font-medium text-sm",
                    projectType === 'technical' ? "text-gray-900" : "text-gray-600"
                  )}>
                    Technical
                  </div>
                  <div className="text-xs text-gray-400">
                    Software dev
                  </div>
                </div>
              </button>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-5 py-2.5 text-gray-600 hover:text-gray-900 font-medium text-sm transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !name}
              className="flex-1 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-sm shadow-blue-500/25"
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {editProject ? 'Saving...' : 'Creating...'}
                </div>
              ) : (
                editProject ? 'Save Changes' : 'Create Project'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function ProjectsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const { projects, isLoading, error, fetchProjects, createProject, updateProject, deleteProject, setCurrentProject } = useProjectStore();
  const [showCreateDialog, setShowCreateDialog] = useState(false);
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
      setShowCreateDialog(false);
      setEditProject(null);
    } else {
      const newProject = await createProject(data);
      if (newProject) {
        setShowCreateDialog(false);
        setCurrentProject(newProject);
        router.push('/kanban');
      }
    }
  };

  const handleEditProject = (project: any) => {
    setEditProject(project);
    setShowCreateDialog(true);
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

  const getProjectTypeColor = (type: string) => {
    return type === 'technical'
      ? 'from-purple-500 to-indigo-600'
      : 'from-amber-500 to-orange-600';
  };

  const getProjectTypeIcon = (type: string) => {
    return type === 'technical'
      ? <FolderKanban className="w-5 h-5" />
      : <Users className="w-5 h-5" />;
  };

  if (!isAuthenticated) return null;

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Projects</h1>
          <p className="text-gray-500 mt-1.5">Manage your projects and requirements</p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search projects..."
              className="pl-12 pr-4 py-2.5 w-full sm:w-72 bg-white border border-gray-200/80 rounded-lg focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none transition-all text-sm shadow-sm"
            />
          </div>

          <button
            onClick={() => setShowCreateDialog(true)}
            className="flex items-center justify-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-medium text-sm shadow-sm shadow-blue-500/25"
          >
            <Plus className="w-5 h-5" />
            New Project
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-50/80 border border-red-200/80 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24">
          <div className="w-10 h-10 border-3 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-4" />
          <p className="text-gray-500 font-medium">Loading projects...</p>
        </div>
      ) : (
        <>
          {filteredProjects.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 text-center bg-white rounded-lg border border-gray-200/60">
              <div className="w-24 h-24 bg-gray-50 rounded-3xl flex items-center justify-center mb-6">
                <FolderKanban className="w-12 h-12 text-gray-300" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2 tracking-tight">
                {searchQuery ? 'No projects found' : 'No projects yet'}
              </h3>
              <p className="text-gray-500 mb-8 max-w-md">
                {searchQuery
                  ? 'Try adjusting your search query'
                  : 'Create your first project to get started with requirement management'
                }
              </p>
              {!searchQuery && (
                <button
                  onClick={() => setShowCreateDialog(true)}
                  className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-medium text-sm shadow-sm shadow-blue-500/25"
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
                  className="group bg-white rounded-lg shadow-soft hover:shadow-elevated hover:-translate-y-1 transition-all border border-gray-200/60 overflow-hidden animate-fade-in-up"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className={`h-2 bg-gradient-to-r ${getProjectTypeColor(project.project_type)}`} />

                  <div className="p-6">
                    <div className="flex justify-between items-start mb-5">
                      <div className="flex items-center gap-3">
                        <div className={`p-2.5 rounded-lg bg-gradient-to-br ${getProjectTypeColor(project.project_type)} text-white shadow-soft`}>
                          {getProjectTypeIcon(project.project_type)}
                        </div>
                        <div>
                          <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">
                            {project.project_type.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleEditProject(project)}
                          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteProject(project.id)}
                          className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors tracking-tight">
                      {project.name}
                    </h3>

                    {project.description && (
                      <p className="text-gray-500 text-sm mb-6 line-clamp-2 leading-relaxed">
                        {project.description}
                      </p>
                    )}

                    <div className="flex items-center gap-4 text-sm text-gray-400 mb-6">
                      <div className="flex items-center gap-1.5">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {new Date(project.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    <button
                      onClick={() => {
                        setCurrentProject(project);
                        router.push('/kanban');
                      }}
                      className="w-full py-3 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-all"
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
        isOpen={showCreateDialog}
        onClose={() => {
          setShowCreateDialog(false);
          setEditProject(null);
        }}
        onSubmit={handleCreateProject}
        isLoading={isLoading}
        editProject={editProject}
      />
    </div>
  );
}
