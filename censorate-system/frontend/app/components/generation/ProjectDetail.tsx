'use client';

import { useEffect } from 'react';
import { clsx } from 'clsx';
import { useGenerationProjectStore } from '@/app/stores/generationProjectStore';
import { useProjectPolling } from '@/app/hooks/useProjectPolling';
import PipelineProgress from './PipelineProgress';

interface ProjectDetailProps {
  projectId: string;
}

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft - Waiting for confirmation',
  confirmed: 'PRD Confirmed',
  designing: 'Designing Architecture...',
  generating: 'Generating Code...',
  reviewing: 'Reviewing Code...',
  ready: 'Ready for Approval',
  pushing: 'Pushing to GitHub...',
  completed: 'Completed',
  failed: 'Failed',
};

export default function ProjectDetail({ projectId }: ProjectDetailProps) {
  const { currentProject, fetchProject, confirmPRD, approveArchitecture, approveCode, retryProject, cancelProject, isLoading } = useGenerationProjectStore();

  useProjectPolling(projectId);

  useEffect(() => {
    fetchProject(projectId);
  }, [projectId, fetchProject]);

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-3 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
      </div>
    );
  }

  const isActive = ['designing', 'generating', 'reviewing', 'pushing'].includes(currentProject.status);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{currentProject.name}</h1>
        {currentProject.description && (
          <p className="mt-1 text-gray-600">{currentProject.description}</p>
        )}
        <div className="mt-2 flex items-center gap-2">
          <span className={clsx(
            'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
            currentProject.status === 'completed' && 'bg-green-100 text-green-800',
            currentProject.status === 'failed' && 'bg-red-100 text-red-800',
            isActive && 'bg-blue-100 text-blue-800',
            currentProject.status === 'draft' && 'bg-gray-100 text-gray-800',
            currentProject.status === 'ready' && 'bg-amber-100 text-amber-800',
          )}>
            {STATUS_LABELS[currentProject.status] || currentProject.status}
          </span>
        </div>
      </div>

      {/* Error message */}
      {currentProject.error_message && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200">
          <p className="text-sm text-red-700">{currentProject.error_message}</p>
        </div>
      )}

      {/* Pipeline Progress */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Progress</h2>
        <PipelineProgress steps={currentProject.steps || []} />
      </div>

      {/* Action buttons */}
      <div className="flex flex-wrap gap-3">
        {currentProject.status === 'draft' && (
          <button
            onClick={() => confirmPRD(projectId, { confirmed: true })}
            disabled={isLoading}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-xl transition-colors text-sm"
          >
            {isLoading ? 'Processing...' : 'Start Analysis'}
          </button>
        )}

        {currentProject.status === 'confirmed' && (
          <button
            onClick={() => fetchProject(projectId)}
            disabled={isLoading}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors text-sm"
          >
            Check Status
          </button>
        )}

        {currentProject.status === 'ready' && (
          <>
            <button
              onClick={() => approveArchitecture(projectId)}
              disabled={isLoading}
              className="px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white font-medium rounded-xl transition-colors text-sm"
            >
              {isLoading ? 'Processing...' : 'Start Code Generation'}
            </button>
            <button
              onClick={() => cancelProject(projectId)}
              disabled={isLoading}
              className="px-6 py-2.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium rounded-xl transition-colors text-sm"
            >
              Cancel
            </button>
          </>
        )}

        {currentProject.status === 'failed' && (
          <>
            <button
              onClick={() => retryProject(projectId)}
              disabled={isLoading}
              className="px-6 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-xl transition-colors text-sm"
            >
              {isLoading ? 'Retrying...' : 'Retry Pipeline'}
            </button>
            <button
              onClick={() => cancelProject(projectId)}
              disabled={isLoading}
              className="px-6 py-2.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium rounded-xl transition-colors text-sm"
            >
              Reset to Draft
            </button>
          </>
        )}

        {currentProject.status === 'completed' && currentProject.repo_url && (
          <a
            href={currentProject.repo_url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-2.5 bg-gray-900 hover:bg-gray-800 text-white font-medium rounded-xl transition-colors text-sm inline-flex items-center gap-2"
          >
            View on GitHub
          </a>
        )}
      </div>

      {/* Generated files */}
      {currentProject.files && currentProject.files.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Generated Files ({currentProject.files.length})</h2>
          <div className="grid gap-2">
            {currentProject.files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between px-4 py-2.5 bg-gray-50 rounded-xl"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-sm text-gray-500 font-mono truncate">{file.file_path}</span>
                  {file.language && (
                    <span className="text-xs text-gray-400 uppercase">{file.language}</span>
                  )}
                </div>
                <span className={clsx(
                  'text-xs font-medium px-2 py-0.5 rounded-full',
                  file.status === 'approved' && 'bg-green-100 text-green-700',
                  file.status === 'auto_fixed' && 'bg-blue-100 text-blue-700',
                  file.status === 'needs_review' && 'bg-amber-100 text-amber-700',
                  file.status === 'generated' && 'bg-gray-100 text-gray-600',
                )}>
                  {file.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
