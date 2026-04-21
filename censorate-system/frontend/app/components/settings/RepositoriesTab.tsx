'use client';

import { useState, useEffect } from 'react';
import { useProjectStore } from '@/app/stores/projectStore';
import { githubReposAPI, GitHubRepo } from '@/lib/api/githubRepos';
import { Plus, Trash2, GitBranch, ExternalLink, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';

export default function RepositoriesTab() {
  const { currentProject } = useProjectStore();
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({ url: '', description: '' });

  useEffect(() => {
    if (currentProject) {
      fetchRepos();
    }
  }, [currentProject]);

  const fetchRepos = async () => {
    if (!currentProject) return;
    setIsLoading(true);
    try {
      const data = await githubReposAPI.listRepos(currentProject.id);
      setRepos(data);
    } catch (error) {
      console.error('Failed to fetch repos:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddRepo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentProject || !formData.url.trim()) return;

    setIsSubmitting(true);
    try {
      const newRepo = await githubReposAPI.addRepo(currentProject.id, {
        url: formData.url.trim(),
        description: formData.description.trim() || undefined
      });
      setRepos(prev => [...prev, newRepo]);
      setFormData({ url: '', description: '' });
      setShowAddForm(false);
    } catch (error) {
      console.error('Failed to add repo:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteRepo = async (repoId: string) => {
    if (!currentProject) return;
    if (!confirm('Are you sure you want to remove this repository?')) return;

    try {
      await githubReposAPI.deleteRepo(currentProject.id, repoId);
      setRepos(prev => prev.filter(r => r.id !== repoId));
    } catch (error) {
      console.error('Failed to delete repo:', error);
    }
  };

  const getDomainFromUrl = (url: string) => {
    try {
      const urlObj = new URL(url.startsWith('http') ? url : `https://${url}`);
      return urlObj.hostname + urlObj.pathname;
    } catch {
      return url;
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6 items-start sm:items-center justify-between">
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            Git Repositories
          </h3>
          <p className="text-sm text-slate-600">
            Connect Git repositories to your project
          </p>
        </div>

        {!showAddForm && (
          <button
            onClick={() => setShowAddForm(true)}
            className="inline-flex items-center gap-2 px-5 py-3 bg-slate-600 text-white rounded-xl hover:bg-slate-700 transition-all duration-200 font-medium text-sm shadow-md hover:shadow-lg"
          >
            <Plus size={16} strokeWidth={2} />
            Add Repository
          </button>
        )}
      </div>

      {/* Add Form */}
      {showAddForm && (
        <div className="bg-slate-50/70 border border-slate-200/60 rounded-2xl p-6 mb-6 shadow-sm">
          <form onSubmit={handleAddRepo} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">
                Repository URL
              </label>
              <input
                type="text"
                value={formData.url}
                onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                placeholder="https://github.com/username/repository"
                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-300 focus:border-slate-400 outline-none transition-all duration-200 text-slate-700 text-sm shadow-sm"
                autoFocus
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">
                Description (Optional)
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Brief description of this repository"
                rows={2}
                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-300 focus:border-slate-400 outline-none transition-all duration-200 text-slate-700 text-sm resize-none shadow-sm"
              />
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                type="submit"
                disabled={isSubmitting || !formData.url.trim()}
                className={clsx(
                  'inline-flex items-center gap-2 px-6 py-3 rounded-xl font-medium text-sm transition-all duration-200',
                  isSubmitting || !formData.url.trim()
                    ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                    : 'bg-slate-600 text-white hover:bg-slate-700 shadow-md hover:shadow-lg'
                )}
              >
                {isSubmitting ? (
                  <Loader2 size={17} className="animate-spin" />
                ) : (
                  <GitBranch size={17} strokeWidth={2} />
                )}
                {isSubmitting ? 'Adding...' : 'Add Repository'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false);
                  setFormData({ url: '', description: '' });
                }}
                className="px-6 py-3 text-slate-500 hover:text-slate-700 text-sm font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Repositories List */}
      {isLoading ? (
        <div className="flex justify-center py-14">
          <div className="animate-spin w-8 h-8 border-2 border-slate-200 rounded-full border-t-slate-500" />
        </div>
      ) : repos.length === 0 ? (
        <div className="bg-slate-50/70 border border-slate-200/60 rounded-2xl p-12 text-center shadow-sm">
          <div className="w-16 h-16 bg-slate-100 border border-slate-200/50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
            <GitBranch size={32} className="text-slate-400" />
          </div>
          <h3 className="text-lg font-medium text-slate-700 mb-2">
            No repositories connected
          </h3>
          <p className="text-slate-500 text-sm">
            Connect Git repositories to integrate with your project
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {repos.map((repo) => (
            <div
              key={repo.id}
              className="bg-slate-50/70 border border-slate-200/60 rounded-2xl p-5 flex items-start justify-between gap-4 shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <div className="flex items-start gap-4 flex-1 min-w-0">
                <div className="w-12 h-12 bg-white border border-slate-200 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                  <GitBranch size={22} className="text-slate-500" />
                </div>
                <div className="min-w-0 flex-1">
                  <a
                    href={repo.url.startsWith('http') ? repo.url : `https://${repo.url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-base font-semibold text-slate-700 hover:text-slate-900 transition-colors flex items-center gap-1.5 truncate"
                  >
                    <span className="truncate">{getDomainFromUrl(repo.url)}</span>
                    <ExternalLink size={14} className="flex-shrink-0 text-slate-400" />
                  </a>
                  {repo.description && (
                    <p className="text-sm text-slate-600 mt-1.5 line-clamp-2">
                      {repo.description}
                    </p>
                  )}
                  <p className="text-xs text-slate-400 mt-2.5">
                    Added {new Date(repo.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDeleteRepo(repo.id)}
                className="p-2.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors flex-shrink-0"
                title="Remove repository"
              >
                <Trash2 size={19} strokeWidth={1.5} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
