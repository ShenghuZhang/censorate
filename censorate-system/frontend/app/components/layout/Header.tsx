'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Menu,
  Search,
  Bell,
  User,
  Plus,
  FolderKanban,
  ChevronDown,
  MoreHorizontal,
  Pencil,
  Trash2,
  HelpCircle,
  LogOut,
  UserCircle
} from 'lucide-react';
import { useProjectStore } from '@/app/stores/projectStore';
import { useAuth } from '@/app/hooks/useAuth';
import { useNotificationStore } from '@/app/stores/notificationStore';
import { clsx } from 'clsx';
import NotificationDropdown from '../notifications/NotificationDropdown';

interface HeaderProps {
  onMenuClick: () => void;
}

interface CreateProjectDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  isLoading: boolean;
}

import SwimlaneSelector, { DEFAULT_LANES } from '@/app/components/settings/SwimlaneSelector';

function CreateProjectDialog({ isOpen, onClose, onSubmit, isLoading }: CreateProjectDialogProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [swimlanes, setSwimlanes] = useState<string[]>(DEFAULT_LANES);

  useEffect(() => {
    if (!isOpen) {
      setName('');
      setDescription('');
      setSwimlanes(DEFAULT_LANES);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      name,
      description,
      project_type: 'non_technical',
      settings: { swimlanes }
    });
  };

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-8 border border-gray-200">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">New Project</h2>
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
              className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-sm"
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
              className="w-full px-4 py-2.5 bg-gray-50/80 border border-gray-200/80 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none transition-all text-sm resize-none"
              rows={3}
              placeholder="Enter project description"
            />
          </div>

          <SwimlaneSelector value={swimlanes} onChange={setSwimlanes} />

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
              className="flex-1 px-5 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-sm shadow-blue-500/25"
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating...
                </div>
              ) : (
                'Create Project'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function UserDropdown({ isOpen, onClose, onLogout }: {
  isOpen: boolean;
  onClose: () => void;
  onLogout: () => void;
}) {
  const router = useRouter();
  const { user } = useAuth();

  if (!isOpen) return null;

  const userAlias = user?.name || (user?.email ? user.email.split('@')[0] : 'User');

  return (
    <>
      <div className="fixed inset-0 z-[60]" onClick={onClose} />

      <div className="absolute top-full right-0 mt-2 w-72 bg-white rounded-2xl shadow-xl border border-gray-200 z-[70] overflow-hidden">
        {/* User Info Header */}
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-medium shadow-sm">
              <User size={24} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">
                {userAlias}
              </p>
              <p className="text-xs text-gray-400 truncate">
                {user?.email}
              </p>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <div className="py-2">
          <button
            onClick={() => {
              router.push('/profile');
              onClose();
            }}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <UserCircle size={18} className="text-gray-400" />
            <span>Profile</span>
          </button>

          <div className="border-t border-gray-100 my-2" />

          <button
            onClick={() => {
              onLogout();
              onClose();
            }}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut size={18} className="text-red-400" />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </>
  );
}

export default function Header({ onMenuClick }: HeaderProps) {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { projects, currentProject, isLoading, fetchProjects, createProject, setCurrentProject, deleteProject } = useProjectStore();
  const { notifications, unreadCount, isOpen: isNotificationsOpen, setIsOpen: setNotificationsOpen } = useNotificationStore();

  const [isProjectSelectorOpen, setIsProjectSelectorOpen] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleCreateProject = async (data: any) => {
    const newProject = await createProject(data);
    if (newProject) {
      setIsCreateDialogOpen(false);
      setCurrentProject(newProject);
    }
  };

  const handleSelectProject = (project: any) => {
    setCurrentProject(project);
    setIsProjectSelectorOpen(false);
  };

  const handleDeleteProject = async (e: React.MouseEvent, projectId: string) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this project?')) {
      await deleteProject(projectId);
    }
  };

  const getProjectTypeColor = (type: string) => {
    return type === 'technical'
      ? 'from-purple-500 to-indigo-600'
      : 'from-amber-500 to-orange-500';
  };

  const userAlias = user?.name || (user?.email ? user.email.split('@')[0] : 'User');

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-50">
      <div className="flex items-center justify-between max-w-full">
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 hover:bg-gray-100 rounded-xl transition-colors focus:outline-none"
          >
            <Menu size={20} className="text-gray-600" />
          </button>

          <div className="relative">
            <button
              onClick={() => setIsProjectSelectorOpen(!isProjectSelectorOpen)}
              className="flex items-center gap-2 px-4 py-2 hover:bg-gray-100 rounded-xl transition-colors group focus:outline-none"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-sm">
                <FolderKanban className="w-4 h-4 text-white" />
              </div>
              <div className="text-left hidden sm:block">
                <div className="text-sm font-semibold text-gray-900 tracking-tight">
                  {currentProject?.name || 'Select Project'}
                </div>
                <div className="text-xs text-gray-400">
                  {currentProject ? currentProject.project_type.replace('_', ' ') : 'No project selected'}
                </div>
              </div>
              <ChevronDown className={clsx(
                "w-4 h-4 text-gray-400 transition-transform",
                isProjectSelectorOpen && "rotate-180"
              )} />
            </button>

            {isProjectSelectorOpen && (
              <>
                <div className="fixed inset-0 z-[60]" onClick={() => setIsProjectSelectorOpen(false)} />
                <div className="absolute top-full left-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-gray-200 z-[70] overflow-hidden">
                  <div className="p-3 border-b border-gray-100">
                    <button
                      onClick={() => {
                        setIsProjectSelectorOpen(false);
                        setIsCreateDialogOpen(true);
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-gray-50 rounded-xl transition-colors text-sm font-medium text-blue-600"
                    >
                      <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                        <Plus className="w-4 h-4 text-blue-600" />
                      </div>
                      New Project
                    </button>
                  </div>

                  <div className="max-h-80 overflow-y-auto">
                    {isLoading ? (
                      <div className="p-8 text-center">
                        <div className="w-6 h-6 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin mx-auto mb-2" />
                        <p className="text-sm text-gray-400">Loading projects...</p>
                      </div>
                    ) : projects.length === 0 ? (
                      <div className="p-8 text-center">
                        <div className="w-12 h-12 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
                          <FolderKanban className="w-6 h-6 text-gray-300" />
                        </div>
                        <p className="text-sm text-gray-500 mb-1">No projects yet</p>
                        <p className="text-xs text-gray-400">Create one to get started</p>
                      </div>
                    ) : (
                      <div className="py-2">
                        {projects.map((project) => (
                          <div
                            key={project.id}
                            className="group relative"
                          >
                            <button
                              onClick={() => handleSelectProject(project)}
                              className={clsx(
                                "w-full flex items-center gap-3 px-3 py-2.5 transition-colors text-left",
                                currentProject?.id === project.id
                                  ? "bg-blue-50"
                                  : "hover:bg-gray-50"
                              )}
                            >
                              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getProjectTypeColor(project.project_type)} flex items-center justify-center shadow-sm`}>
                                <FolderKanban className="w-5 h-5 text-white" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className={clsx(
                                  "text-sm font-semibold truncate tracking-tight",
                                  currentProject?.id === project.id
                                    ? "text-blue-900"
                                    : "text-gray-900"
                                )}>
                                  {project.name}
                                </div>
                                <div className="text-xs text-gray-400 truncate">
                                  {project.project_type.replace('_', ' ')} • {new Date(project.created_at).toLocaleDateString()}
                                </div>
                              </div>
                              {currentProject?.id === project.id && (
                                <div className="w-2 h-2 rounded-full bg-blue-500" />
                              )}
                            </button>

                            <div className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button
                                onClick={(e) => handleDeleteProject(e, project.id)}
                                className="p-1.5 hover:bg-red-50 rounded-lg text-gray-400 hover:text-red-500 transition-colors"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="p-3 border-t border-gray-100">
                    <button
                      onClick={() => router.push('/projects')}
                      className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-xl transition-colors"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                      Manage Projects
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden md:flex items-center bg-gray-100 rounded-xl px-3 py-2">
            <Search size={18} className="text-gray-400 mr-2" />
            <input
              type="text"
              placeholder="Search..."
              className="bg-transparent border-none outline-none text-sm text-gray-700 placeholder-gray-400 w-44"
            />
          </div>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setNotificationsOpen(!isNotificationsOpen)}
              className="p-2.5 hover:bg-gray-100 rounded-xl transition-colors relative focus:outline-none"
            >
              <Bell size={20} className="text-gray-600" />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-5 h-5 bg-red-500 rounded-full text-white text-xs font-bold flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            <NotificationDropdown
              isOpen={isNotificationsOpen}
              onClose={() => setNotificationsOpen(false)}
            />
          </div>

          {/* Help Icon */}
          <button className="p-2.5 hover:bg-gray-100 rounded-xl transition-colors focus:outline-none">
            <HelpCircle size={20} className="text-gray-600" />
          </button>

          {/* User Avatar with Dropdown */}
          <div className="relative pl-2">
            <button
              onClick={() => setIsUserDropdownOpen(!isUserDropdownOpen)}
              className="flex items-center gap-3 px-2 py-1.5 hover:bg-gray-100 rounded-xl transition-colors focus:outline-none"
            >
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900">{userAlias}</p>
              </div>
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-medium shadow-sm">
                <User size={18} />
              </div>
            </button>

            <UserDropdown
              isOpen={isUserDropdownOpen}
              onClose={() => setIsUserDropdownOpen(false)}
              onLogout={logout}
            />
          </div>
        </div>
      </div>

      <CreateProjectDialog
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        onSubmit={handleCreateProject}
        isLoading={isLoading}
      />
    </header>
  );
}
