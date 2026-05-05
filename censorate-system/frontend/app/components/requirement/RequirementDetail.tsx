'use client';

import { useState, useEffect } from 'react';
import { X, Edit, Paperclip, Clock, User, GitCommit, CheckCircle2 } from 'lucide-react';
import { Requirement, useRequirementStore } from '@/app/stores/requirementStore';
import { useAuthStore } from '@/app/stores/authStore';
import HtmlRenderer from '../common/HtmlRenderer';
import RichTextEditor from '../common/RichTextEditor';
import CommentInput from './CommentInput';

interface RequirementDetailProps {
  requirement: Requirement;
  onClose?: () => void;
  mode?: 'modal' | 'page';
}

// Format date to GitHub-style relative time
const formatTimeAgo = (dateString: string | Date) => {
  if (!dateString) {
    return 'unknown time';
  }

  let date: Date;

  if (typeof dateString === 'string') {
    if (!dateString.includes('Z') && !dateString.includes('+')) {
      date = new Date(dateString + 'Z');
    } else {
      date = new Date(dateString);
    }
  } else {
    date = dateString;
  }

  if (isNaN(date.getTime())) {
    return 'unknown time';
  }

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMs < 0) {
    const absMins = Math.abs(diffMins);
    if (absMins < 60) {
      return 'just now';
    }
  }

  if (diffMins < 1) {
    return 'just now';
  } else if (diffMins < 60) {
    return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  } else if (diffDays < 30) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  } else {
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
};

export default function RequirementDetail({ requirement: propRequirement, onClose, mode = 'modal' }: RequirementDetailProps) {
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [savedDescription, setSavedDescription] = useState<string | null>(null);
  const { comments, fetchComments, addComment, statusHistory, fetchHistory, updateRequirement, selectedRequirement } = useRequirementStore();

  const requirement = (mode === 'page' && selectedRequirement?.id === propRequirement.id)
    ? selectedRequirement
    : propRequirement;

  const displayDescription = savedDescription !== null ? savedDescription : requirement.description;

  useEffect(() => {
    if (requirement.id) {
      fetchComments(requirement.id);
      fetchHistory(requirement.id);
    }
  }, [requirement.id, fetchComments, fetchHistory]);

  const handleSaveDescription = async () => {
    try {
      const editorElement = document.querySelector('[contenteditable="true"]');
      const content = editorElement?.innerHTML || '';
      setSavedDescription(content);
      await updateRequirement(requirement.id, { description: content });
      setIsEditingDescription(false);
    } catch (error) {
      console.error('Failed to save description:', error);
    }
  };

  const handleAddComment = async (content: string) => {
    try {
      const authState = useAuthStore.getState();
      const user = authState.user;
      const authorName = user?.name || user?.email?.split('@')[0] || 'User';

      await addComment(requirement.id, {
        content,
        authorName,
        authorId: user?.id,
        isAi: false,
      });
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  const formatStatus = (status: string) => {
    return status.replace('_', ' ').toUpperCase();
  };

  const formatAssignee = () => {
    if (requirement.assignedToName || requirement.assignedTo) {
      return `Assigned to ${requirement.assignedToName || requirement.assignedTo}`;
    }
    return 'Unassigned';
  };

  const displayComments = [...comments].sort((a, b) => {
    const dateA = a.createdAt ? new Date(a.createdAt) : new Date();
    const dateB = b.createdAt ? new Date(b.createdAt) : new Date();
    return dateB.getTime() - dateA.getTime();
  });

  const displayHistory = [...statusHistory].sort((a, b) => {
    const dateA = new Date(a.createdAt);
    const dateB = new Date(b.createdAt);
    return dateB.getTime() - dateA.getTime();
  });

  const getStateColor = (status: string) => {
    const s = status.toLowerCase();
    if (s.includes('todo') || s.includes('backlog')) return 'bg-gray-500';
    if (s.includes('progress') || s.includes('design') || s.includes('analysis')) return 'bg-blue-500';
    if (s.includes('review') || s.includes('testing')) return 'bg-purple-500';
    if (s.includes('done') || s.includes('complete') || s.includes('deployed')) return 'bg-green-500';
    return 'bg-gray-500';
  };

  const Content = () => (
    <div className="flex flex-col lg:flex-row bg-[#f6f8fa]">
      {/* Left column - Main content */}
      <div className="flex-1 min-w-0">
        {/* Main content area */}
        <div className="p-4 lg:p-6">
          {/* Description section */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-[#1f2328]">Description</h2>
              <button
                onClick={() => {
                  if (isEditingDescription) {
                    handleSaveDescription();
                  } else {
                    setSavedDescription(null);
                    setIsEditingDescription(true);
                  }
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-[#1f2328] bg-white border border-[#d0d7de] rounded-md hover:bg-[#f6f8fa] hover:border-[#d0d7de] transition-colors"
              >
                <Edit size={14} />
                {isEditingDescription ? 'Save' : 'Edit'}
              </button>
            </div>

            {isEditingDescription ? (
              <div className="border border-[#d0d7de] rounded-md overflow-hidden bg-white">
                <RichTextEditor
                  value={requirement.description || ''}
                  placeholder="Add a description..."
                  minHeight="200px"
                  requirementId={requirement.id}
                />
              </div>
            ) : (
              <div className="border border-[#d0d7de] rounded-md bg-white p-4">
                <div className="text-[#1f2328]">
                  {displayDescription ? (
                    <HtmlRenderer content={displayDescription} />
                  ) : (
                    <p className="text-[#656d76]">No description provided.</p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Discussions section */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <h2 className="text-base font-semibold text-[#1f2328]">Discussions</h2>
              <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium text-[#1f2328] bg-[#e6edf3] border border-[#d0d7de]">
                {displayComments.length}
              </span>
            </div>

            {/* Comment input */}
            <div className="mb-6">
              <CommentInput
                onSubmit={handleAddComment}
                placeholder="Add a comment..."
                requirementId={requirement.id}
              />
            </div>

            {/* Comments list */}
            <div className="space-y-6">
              {displayComments.map((comment: any) => (
                <div key={comment.id} className="flex gap-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-[#0969da] flex items-center justify-center text-white text-xs font-semibold">
                      {comment.authorName?.[0]?.toUpperCase() || 'U'}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="border border-[#d0d7de] rounded-md">
                      <div className="flex items-center gap-2 px-4 py-2 bg-[#f6f8fa] border-b border-[#d0d7de] rounded-t-md">
                        <span className="font-semibold text-[#1f2328] text-sm">{comment.authorName || comment.user || 'User'}</span>
                        <span className="text-[#656d76] text-xs">
                          commented {comment.createdAt ? formatTimeAgo(comment.createdAt) : ''}
                        </span>
                      </div>
                      <div className="p-4 text-[#1f2328] text-sm">
                        {comment.content && typeof comment.content === 'string' ? (
                          <HtmlRenderer content={comment.content} />
                        ) : (
                          <p>{comment.content || ''}</p>
                        )}
                      </div>
                      {comment.attachments && comment.attachments.length > 0 && (
                        <div className="px-4 pb-4">
                          <div className="flex flex-wrap gap-2">
                            {comment.attachments.map((file: string, idx: number) => (
                              <div key={idx} className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#f6f8fa] border border-[#d0d7de] rounded-md">
                                <Paperclip size={12} className="text-[#656d76]" />
                                <span className="text-xs text-[#1f2328]">{file}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right column - Sidebar */}
      <div className="w-full lg:w-80 flex-shrink-0 border-l border-[#d0d7de] bg-[#f6f8fa]">
        <div className="p-4 lg:p-6 space-y-6">
          {/* Properties section */}
          <div>
            <h2 className="text-sm font-semibold text-[#1f2328] mb-3">Properties</h2>
            <div className="space-y-4">
              <div>
                <dt className="text-xs font-medium text-[#656d76] mb-1">Priority</dt>
                <dd>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${
                    requirement.priority === 'high'
                      ? 'bg-red-100 text-red-800 border border-red-300'
                      : requirement.priority === 'medium'
                      ? 'bg-blue-100 text-blue-800 border border-blue-300'
                      : 'bg-gray-100 text-gray-800 border border-gray-300'
                  }`}>
                    {requirement.priority.toUpperCase()}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-[#656d76] mb-1">Sprint</dt>
                <dd className="text-sm text-[#1f2328]">V1 Core Layout</dd>
              </div>
            </div>
          </div>

          <hr className="border-[#d0d7de]" />

          {/* Activity History */}
          <div>
            <h2 className="text-sm font-semibold text-[#1f2328] mb-3">Activity History</h2>
            <div className="space-y-0">
              {displayHistory.length > 0 ? (
                displayHistory.map((history: any, idx: number) => (
                  <div key={history.id} className="relative pl-6 pb-4">
                    {idx < displayHistory.length - 1 && (
                      <div className="absolute left-[7px] top-5 bottom-0 w-px bg-[#d0d7de]" />
                    )}
                    <div className={`absolute left-0 top-1.5 w-3 h-3 rounded-full border-2 border-white ${
                      history.fromStatus ? 'bg-blue-500 border-blue-500' : 'bg-green-500 border-green-500'
                    }`} />
                    <div>
                      <p className="text-sm text-[#1f2328]">
                        {history.fromStatus ? 'Status Changed' : 'Requirement Created'}
                      </p>
                      <p className="text-xs text-[#656d76] mt-0.5">
                        {history.changedByName || history.changedBy || 'System'} • {formatTimeAgo(history.createdAt)}
                      </p>
                      {history.fromStatus && history.toStatus && (
                        <p className="text-xs text-[#656d76] mt-1">
                          <code className="px-1 py-0.5 bg-[#e6edf3] rounded text-xs">{history.fromStatus.replace('_', ' ')}</code>
                          <span className="mx-1">→</span>
                          <code className="px-1 py-0.5 bg-[#e6edf3] rounded text-xs">{history.toStatus.replace('_', ' ')}</code>
                        </p>
                      )}
                      {history.note && (
                        <p className="text-xs text-[#656d76] mt-1 italic">{history.note}</p>
                      )}
                      {history.assignedToName || history.assignedTo ? (
                        <p className="text-xs text-[#656d76] mt-1">
                          Assigned to: {history.assignedToName || history.assignedTo}
                        </p>
                      ) : null}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-[#656d76]">No activity yet</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (mode === 'page') {
    return (
      <div className="min-h-screen bg-[#f6f8fa]">
        {/* Header */}
        <div className="bg-white border-b border-[#d0d7de]">
          <div className="max-w-7xl mx-auto px-4 lg:px-6 py-4">
            {/* Top bar with REQ number and status */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold text-[#656d76] bg-[#f6f8fa] border border-[#d0d7de]">
                  REQ-{requirement.reqNumber}
                </span>
                <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium text-white ${getStateColor(requirement.status)}`}>
                  <CheckCircle2 size={12} />
                  {formatStatus(requirement.status)}
                </span>
              </div>
            </div>

            {/* Title */}
            <h1 className="text-2xl font-semibold text-[#1f2328] mb-3 leading-tight">
              {requirement.title}
            </h1>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-[#656d76]">
              <div className="flex items-center gap-1.5">
                <User size={14} />
                <span>{formatAssignee()}</span>
              </div>
              {requirement.expectedCompletionAt && (
                <div className="flex items-center gap-1.5">
                  <Clock size={14} />
                  <span>Due {new Date(requirement.expectedCompletionAt).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto">
          <Content />
        </div>
      </div>
    );
  }

  // Modal mode
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-6xl max-h-[95vh] overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="bg-white border-b border-[#d0d7de] px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold text-[#656d76] bg-[#f6f8fa] border border-[#d0d7de]">
              REQ-{requirement.reqNumber}
            </span>
            <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium text-white ${getStateColor(requirement.status)}`}>
              <CheckCircle2 size={12} />
              {formatStatus(requirement.status)}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-[#f6f8fa] rounded-md transition-colors"
          >
            <X size={18} className="text-[#656d76]" />
          </button>
        </div>

        <div className="bg-white px-4 py-4 border-b border-[#d0d7de]">
          <h2 className="text-xl font-semibold text-[#1f2328] mb-3">{requirement.title}</h2>
          <div className="flex flex-wrap items-center gap-4 text-sm text-[#656d76]">
            <div className="flex items-center gap-1.5">
              <User size={14} />
              <span>{formatAssignee()}</span>
            </div>
            {requirement.expectedCompletionAt && (
              <div className="flex items-center gap-1.5">
                <Clock size={14} />
                <span>Due {new Date(requirement.expectedCompletionAt).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <Content />
        </div>
      </div>
    </div>
  );
}
