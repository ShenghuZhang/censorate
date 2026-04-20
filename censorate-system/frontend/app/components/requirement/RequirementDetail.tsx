'use client';

import { useState } from 'react';
import { X, Edit, Paperclip, AtSign, Clock, User } from 'lucide-react';
import { Requirement } from '@/app/stores/requirementStore';

interface RequirementDetailProps {
  requirement: Requirement;
  onClose: () => void;
}

// Mock data for demonstration
const mockComments = [
  {
    id: 1,
    user: 'Julian Rossi',
    avatar: 'JR',
    time: '2 hours ago',
    content: 'This looks great. Let\'s schedule a review for tomorrow.',
    attachments: []
  },
  {
    id: 2,
    user: 'Sarah Chen',
    avatar: 'SC',
    time: '1 hour ago',
    content: 'I\'ve attached the design spec for reference.',
    attachments: ['design-spec-v2.pdf']
  }
];

const mockActivities = [
  {
    id: 1,
    type: 'created',
    title: 'Requirement Created',
    user: 'Alex Kim',
    time: '3 days ago'
  },
  {
    id: 2,
    type: 'status',
    title: 'Status Changed',
    user: 'System',
    time: '2 days ago',
    detail: 'Backlog → Todo'
  },
  {
    id: 3,
    type: 'collaborator',
    title: 'Collaborator Added',
    user: 'Alex Kim',
    time: '1 day ago',
    detail: 'Julian Rossi'
  },
  {
    id: 4,
    type: 'file',
    title: 'File Attached',
    user: 'Sarah Chen',
    time: '1 hour ago',
    detail: 'design-spec-v2.pdf'
  }
];

export default function RequirementDetail({ requirement, onClose }: RequirementDetailProps) {
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [commentText, setCommentText] = useState('');

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-white rounded-3xl w-full max-w-6xl max-h-[95vh] overflow-hidden shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-8 pt-6 pb-4 border-b border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="bg-gray-100 text-sm font-bold px-4 py-1.5 rounded-full">
                REQ-{requirement.reqNumber}
              </span>
              <span className="text-sm text-gray-500 font-medium tracking-wide">
                {requirement.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
              <X size={20} className="text-gray-500" />
            </button>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-3">{requirement.title}</h1>

          <div className="flex items-center gap-6 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <User size={16} />
              <span>Assigned to Julian Rossi</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock size={16} />
              <span>Updated 2 hours ago</span>
            </div>
          </div>
        </div>

        {/* Content - Two column layout */}
        <div className="flex flex-col lg:flex-row overflow-hidden">
          {/* Left column - Main content */}
          <div className="flex-1 overflow-y-auto p-8 max-h-[calc(95vh-140px)]">
            {/* Description section */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-bold text-gray-400 tracking-widest uppercase">Description</h2>
                <button
                  onClick={() => setIsEditingDescription(!isEditingDescription)}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
                >
                  <Edit size={14} />
                  Edit Content
                </button>
              </div>
              <div className="text-gray-700 leading-relaxed">
                {requirement.description || 'No description provided.'}
                <div className="mt-4 space-y-2">
                  <div className="flex items-start gap-2">
                    <span className="text-gray-400 mt-1">•</span>
                    <span>Support multiple animation formats (Lottie, Rive, GIF)</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-gray-400 mt-1">•</span>
                    <span>Timeline editor with keyframe manipulation</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-gray-400 mt-1">•</span>
                    <span>Preview controls with scrubbing support</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Discussions section */}
            <div>
              <div className="flex items-center gap-2 mb-6">
                <h2 className="text-sm font-bold text-gray-400 tracking-widest uppercase">Discussions</h2>
                <span className="bg-gray-100 text-gray-600 text-xs font-semibold px-2 py-0.5 rounded-full">
                  {mockComments.length}
                </span>
              </div>

              {/* Comment input */}
              <div className="flex gap-3 mb-6">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold flex-shrink-0">
                  Y
                </div>
                <div className="flex-1">
                  <textarea
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Add a comment..."
                    className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none resize-none text-sm"
                    rows={3}
                  />
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center gap-1">
                      <button className="p-2 hover:bg-gray-100 rounded-xl transition-colors text-gray-500">
                        <Paperclip size={18} />
                      </button>
                      <button className="p-2 hover:bg-gray-100 rounded-xl transition-colors text-gray-500">
                        <AtSign size={18} />
                      </button>
                    </div>
                    <button
                      disabled={!commentText.trim()}
                      className="px-4 py-2 bg-gray-900 text-white rounded-xl text-sm font-medium hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      Post Comment
                    </button>
                  </div>
                </div>
              </div>

              {/* Comments list */}
              <div className="space-y-6">
                {mockComments.map(comment => (
                  <div key={comment.id} className="flex gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
                      {comment.avatar}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-gray-900 text-sm">{comment.user}</span>
                        <span className="text-gray-400 text-xs">{comment.time}</span>
                      </div>
                      <p className="text-gray-700 text-sm leading-relaxed">{comment.content}</p>
                      {comment.attachments.length > 0 && (
                        <div className="mt-3 flex gap-2">
                          {comment.attachments.map((file, idx) => (
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
                  <div>
                    <span className="text-xs text-gray-500 font-medium mb-1 block">Tag</span>
                    <div className="flex flex-wrap gap-1.5">
                      <span className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-bold">R&D</span>
                      <span className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-bold">CORE</span>
                    </div>
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
                  {mockActivities.map((activity, idx) => (
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
                        <p className="text-xs text-gray-500 mt-0.5">{activity.user} • {activity.time}</p>
                        {activity.detail && (
                          <p className="text-xs text-gray-400 mt-1">{activity.detail}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <button className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors">
                  View Full Log
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
