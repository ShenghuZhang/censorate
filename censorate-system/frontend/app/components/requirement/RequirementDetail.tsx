'use client';

import { useState, useEffect, useRef } from 'react';
import { X, Edit, Paperclip, Clock, User } from 'lucide-react';
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

// Mock data for activities - use real timestamps
const mockActivities = [
  {
    id: '1',
    type: 'created',
    title: 'Requirement Created',
    user: 'Alex Kim',
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: '2',
    type: 'status',
    title: 'Status Changed',
    user: 'System',
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    detail: 'Backlog → Todo'
  },
  {
    id: '3',
    type: 'comment',
    title: 'Comment Added',
    user: 'Julian Rossi',
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    detail: 'Commented on @REQ-5'
  },
  {
    id: '4',
    type: 'collaborator',
    title: 'Collaborator Added',
    user: 'Alex Kim',
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    detail: 'Julian Rossi'
  }
];

// Format date to friendly time display with proper timezone handling
const formatTimeAgo = (dateString: string | Date) => {
  if (!dateString) {
    return 'unknown time';
  }

  let date: Date;

  if (typeof dateString === 'string') {
    // Ensure we parse the date correctly - handle both ISO and other formats
    // If it doesn't have timezone info, treat as UTC
    if (!dateString.includes('Z') && !dateString.includes('+')) {
      date = new Date(dateString + 'Z');
    } else {
      date = new Date(dateString);
    }
  } else {
    date = dateString;
  }

  if (isNaN(date.getTime())) {
    console.warn('Invalid date:', dateString);
    return 'unknown time';
  }

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  // Debug log
  console.log('🕐 Time info:', {
    input: dateString,
    parsed: date.toISOString(),
    now: now.toISOString(),
    diffMinutes: diffMins,
    diffHours,
    localTime: date.toLocaleString()
  });

  // Handle future dates gracefully
  if (diffMs < 0) {
    const absMins = Math.abs(diffMins);
    // If it's less than 1 hour in future, probably just clock drift - show just now
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
  } else {
    // For older dates, use local time with proper format
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
};

export default function RequirementDetail({ requirement: propRequirement, onClose, mode = 'modal' }: RequirementDetailProps) {
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [savedDescription, setSavedDescription] = useState<string | null>(null);
  const { comments, fetchComments, addComment, statusHistory, fetchHistory, updateRequirement, selectedRequirement } = useRequirementStore();

  // Use selectedRequirement from store if available (for page mode), otherwise use prop
  const requirement = (mode === 'page' && selectedRequirement?.id === propRequirement.id)
    ? selectedRequirement
    : propRequirement;

  // Display description - use savedDescription if available (just saved), otherwise use requirement.description
  const displayDescription = savedDescription !== null ? savedDescription : requirement.description;

  useEffect(() => {
    if (requirement.id) {
      fetchComments(requirement.id);
      fetchHistory(requirement.id);
    }
  }, [requirement.id, fetchComments, fetchHistory]);

  const handleSaveDescription = async () => {
    try {
      // Get content directly from editor
      const editorElement = document.querySelector('[contenteditable="true"]');
      const content = editorElement?.innerHTML || '';

      // Save the content locally first for immediate display
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
      console.log('=== handleAddComment ===');
      console.log('Full auth state:', authState);
      console.log('Current user:', user);

      const authorName = user?.name || user?.email?.split('@')[0] || 'User';
      console.log('Using authorName:', authorName);

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

  // Use only real comments from API, sort newest first
  console.log('Comments from store:', comments);
  const displayComments = [...comments].sort((a, b) => {
    const dateA = a.createdAt ? new Date(a.createdAt) : new Date();
    const dateB = b.createdAt ? new Date(b.createdAt) : new Date();
    return dateB.getTime() - dateA.getTime();
  });

  // Sort status history - newest first
  const displayHistory = [...statusHistory].sort((a, b) => {
    const dateA = new Date(a.createdAt);
    const dateB = new Date(b.createdAt);
    return dateB.getTime() - dateA.getTime();
  });

  const Content = () => (
    <div className="flex flex-col lg:flex-row overflow-hidden">
      {/* Left column - Main content */}
      <div className="flex-1 overflow-y-auto p-8">
        {/* Description section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-gray-400 tracking-widest uppercase">Description</h2>
            <button
              onClick={() => {
                if (isEditingDescription) {
                  handleSaveDescription();
                } else {
                  // Clear saved description when starting edit, use latest from requirement
                  setSavedDescription(null);
                  setIsEditingDescription(true);
                }
              }}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
            >
              <Edit size={14} />
              {isEditingDescription ? 'Save' : 'Edit Content'}
            </button>
          </div>

          {isEditingDescription ? (
            <RichTextEditor
              value={requirement.description || ''}
              placeholder="Add a description..."
              minHeight="200px"
            />
          ) : (
            <div className="text-gray-700 leading-relaxed">
              {displayDescription ? (
                <HtmlRenderer content={displayDescription} />
              ) : (
                <p className="text-gray-400">No description provided.</p>
              )}
            </div>
          )}
        </div>

        {/* Discussions section */}
        <div>
          <div className="flex items-center gap-2 mb-6">
            <h2 className="text-sm font-bold text-gray-400 tracking-widest uppercase">Discussions</h2>
            <span className="bg-gray-100 text-gray-600 text-xs font-semibold px-2 py-0.5 rounded-full">
              {displayComments.length}
            </span>
          </div>

          {/* Comment input using CommentInput component */}
          <div className="mb-8">
            <CommentInput
              onSubmit={handleAddComment}
              placeholder="Add a comment..."
            />
          </div>

          {/* Comments list */}
          <div className="space-y-6">
            {displayComments.map((comment: any) => (
              <div key={comment.id} className="flex gap-3">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
                  {comment.avatar || (comment.authorName?.[0]?.toUpperCase() || 'U')}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900 text-sm">{comment.authorName || comment.user || 'User'}</span>
                    <span className="text-gray-400 text-xs">
                      {comment.time || (comment.createdAt ? formatTimeAgo(comment.createdAt) : '')}
                    </span>
                  </div>
                  <div className="text-gray-700 text-sm leading-relaxed">
                    {comment.content && typeof comment.content === 'string' ? (
                      <HtmlRenderer content={comment.content} />
                    ) : (
                      <p>{comment.content || ''}</p>
                    )}
                  </div>
                  {comment.attachments && comment.attachments.length > 0 && (
                    <div className="mt-3 flex gap-2">
                      {comment.attachments.map((file: string, idx: number) => (
                        <div key={idx} className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-xl">
                          <Paperclip size={14} className="text-gray-400" />
                          <span className="text-sm text-gray-600">{file}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right column - Sidebar */}
      <div className="w-full lg:w-80 border-l border-gray-100 overflow-y-auto max-h-[calc(95vh-140px)]">
        <div className="p-6 space-y-6">
          {/* Properties */}
          <div>
            <h2 className="text-sm font-bold text-gray-400 tracking-widest uppercase mb-4">Properties</h2>
            <div className="space-y-4">
              <div>
                <span className="text-xs text-gray-500 font-medium mb-1 block">Priority</span>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${
                  requirement.priority === 'high'
                    ? 'bg-orange-100 text-orange-700'
                    : requirement.priority === 'medium'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {requirement.priority.toUpperCase()}
                </span>
              </div>
              <div>
                <span className="text-xs text-gray-500 font-medium mb-1 block">Sprint</span>
                <span className="text-sm font-medium text-gray-900">V1 Core Layout</span>
              </div>
            </div>
          </div>

          {/* Share Report button */}
          <button className="w-full py-3 bg-gray-900 text-white rounded-2xl text-sm font-semibold hover:bg-gray-800 transition-colors">
            Share Report
          </button>

          {/* Activity History */}
          <div>
            <h2 className="text-sm font-bold text-gray-400 tracking-widest uppercase mb-4">Activity History</h2>
            <div className="space-y-0">
              {displayHistory.length > 0 ? (
                displayHistory.map((history: any, idx: number) => (
                  <div key={history.id} className="relative pl-6 pb-6">
                    {/* Timeline connector */}
                    {idx < displayHistory.length - 1 && (
                      <div className="absolute left-[7px] top-6 bottom-0 w-px bg-gray-200" />
                    )}
                    {/* Timeline dot */}
                    <div className={`absolute left-0 top-1.5 w-3 h-3 rounded-full border-2 ${
                      history.fromStatus ? 'border-blue-500 bg-blue-100' : 'border-gray-300 bg-white'
                    }`} />
                    {/* Content */}
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {history.fromStatus ? 'Status Changed' : 'Requirement Created'}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {history.changedByName || history.changedBy || 'System'} • {formatTimeAgo(history.createdAt)}
                      </p>
                      {history.fromStatus && history.toStatus && (
                        <p className="text-xs text-gray-400 mt-1">
                          {history.fromStatus.replace('_', ' ')} → {history.toStatus.replace('_', ' ')}
                        </p>
                      )}
                      {history.note && (
                        <p className="text-xs text-gray-400 mt-1 italic">{history.note}</p>
                      )}
                      {history.assignedToName || history.assignedTo ? (
                        <p className="text-xs text-gray-400 mt-1">
                          Assigned to: {history.assignedToName || history.assignedTo}
                        </p>
                      ) : null}
                    </div>
                  </div>
                ))
              ) : (
                mockActivities.map((activity, idx) => (
                  <div key={activity.id} className="relative pl-6 pb-6">
                    {/* Timeline connector */}
                    {idx < mockActivities.length - 1 && (
                      <div className="absolute left-[7px] top-6 bottom-0 w-px bg-gray-200" />
                    )}
                    {/* Timeline dot */}
                    <div className="absolute left-0 top-1.5 w-3 h-3 rounded-full border-2 border-gray-300 bg-white" />
                    {/* Content */}
                    <div>
                      <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{activity.user} • {formatTimeAgo(activity.createdAt)}</p>
                      {activity.detail && (
                        <p className="text-xs text-gray-400 mt-1">{activity.detail}</p>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
            {statusHistory.length === 0 && (
              <button className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors">
                View Full Log
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  if (mode === 'page') {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="bg-gray-100 text-sm font-bold px-4 py-1.5 rounded-full">
                REQ-{requirement.reqNumber}
              </span>
              <span className="text-sm text-gray-500 font-medium tracking-wide">
                {formatStatus(requirement.status)}
              </span>
            </div>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-3">{requirement.title}</h1>

          <div className="flex items-center gap-6 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <User size={16} />
              <span>{formatAssignee()}</span>
            </div>
            {requirement.expectedCompletionAt && (
              <div className="flex items-center gap-2">
                <Clock size={16} />
                <span>Due {new Date(requirement.expectedCompletionAt).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>

        <Content />
      </div>
    );
  }

  // Modal mode
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-6xl max-h-[95vh] overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="bg-gray-100 text-sm font-bold px-4 py-1.5 rounded-full">
              REQ-{requirement.reqNumber}
            </span>
            <span className="text-sm text-gray-500 font-medium tracking-wide">
              {formatStatus(requirement.status)}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
          >
            <X size={20} className="text-gray-600" />
          </button>
        </div>

        <div className="bg-white px-6 py-4 border-b border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-3">{requirement.title}</h2>
          <div className="flex items-center gap-6 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <User size={16} />
              <span>{formatAssignee()}</span>
            </div>
            {requirement.expectedCompletionAt && (
              <div className="flex items-center gap-2">
                <Clock size={16} />
                <span>Due {new Date(requirement.expectedCompletionAt).toLocaleDateString()}</span>
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
