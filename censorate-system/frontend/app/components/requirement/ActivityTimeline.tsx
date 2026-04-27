'use client';

import { type RequirementStatusHistory, type Comment } from '@/lib/api/requirements';
import MarkdownRenderer from '../common/MarkdownRenderer';
import { Calendar, Users, MessageSquare, User, Brain } from 'lucide-react';

interface ActivityTimelineProps {
  history: RequirementStatusHistory[];
  comments: Comment[];
}

type TimelineItem = (RequirementStatusHistory | Comment) & {
  type: 'status_change' | 'comment';
  timestamp: Date;
};

export default function ActivityTimeline({ history, comments }: ActivityTimelineProps) {
  // 合并并排序所有活动
  const items: TimelineItem[] = [
    ...history.map(h => ({ ...h, type: 'status_change' as const, timestamp: new Date(h.changedAt) })),
    ...comments.map(c => ({ ...c, type: 'comment' as const, timestamp: new Date(c.createdAt) }))
  ].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

  const formatStatus = (status: string) => {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="space-y-6">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Activity</h3>

      <div className="space-y-4">
        {items.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p>No activity yet</p>
          </div>
        ) : (
          items.map((item, index) => (
            <div key={`${item.type}-${item.id}`} className="relative pl-8">
              {/* Timeline dot */}
              <div
                className="absolute left-0 top-1 w-4 h-4 rounded-full border-2 border-white shadow-sm"
                style={{
                  backgroundColor: item.type === 'status_change' ? '#374151' : '#8b5cf6'
                }}
              />

              {item.type === 'status_change' ? (
                <div>
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-sm font-medium text-gray-900">Status Changed</span>
                    <span className="text-xs text-gray-400">{formatDate(item.timestamp)}</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {item.fromStatus && `${formatStatus(item.fromStatus)} → `}
                    <span className="font-medium">{formatStatus(item.toStatus)}</span>
                  </p>
                  {item.assignedTo && (
                    <p className="text-sm text-gray-600 flex items-center gap-1">
                      <Users size={14} />
                      Assigned to: <span className="font-medium">{item.assignedTo}</span>
                    </p>
                  )}
                  {item.expectedCompletionAt && (
                    <p className="text-sm text-gray-600 flex items-center gap-1">
                      <Calendar size={14} />
                      Expected: <span className="font-medium">{new Date(item.expectedCompletionAt).toLocaleDateString()}</span>
                    </p>
                  )}
                  {item.note && (
                    <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                      <MarkdownRenderer content={item.note} />
                    </div>
                  )}
                  {item.isBackward && (
                    <span className="inline-block mt-1 text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full">
                      Backward transition
                    </span>
                  )}
                </div>
              ) : (
                <div>
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <span className="text-sm font-medium text-gray-900 flex items-center gap-1">
                      {item.isAi ? <Brain size={14} /> : <User size={14} />}
                      {item.authorName || (item.isAi ? 'AI Assistant' : 'Anonymous')}
                    </span>
                    {item.isAi && (
                      <span className="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full">AI</span>
                    )}
                    <span className="text-xs text-gray-400">{formatDate(item.timestamp)}</span>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <MarkdownRenderer content={item.content} />
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
