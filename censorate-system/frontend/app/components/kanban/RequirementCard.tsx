'use client';

import { useState } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { Undo2, Sparkles, ExternalLink } from 'lucide-react';
import { Requirement } from '@/app/stores/requirementStore';
import RequirementDetail from '../requirement/RequirementDetail';

interface RequirementCardProps {
  requirement: Requirement;
  isOverlay?: boolean;
}

export default function RequirementCard({ requirement, isOverlay = false }: RequirementCardProps) {
  const [showDetail, setShowDetail] = useState(false);

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    // Open in new tab
    window.open(`/requirements/${requirement.id}`, '_blank');
  };

  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: requirement.id,
    disabled: isOverlay,
  });

  const style = isOverlay ? undefined : {
    transform: CSS.Transform.toString(transform),
    opacity: isDragging ? 0.3 : 1,
    zIndex: isDragging ? 50 : 'auto',
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-orange-100 text-orange-700';
      case 'medium':
        return 'bg-blue-100 text-blue-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const cardContent = (
    <>
      {/* Card ID and View button */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm font-bold">
          REQ-{requirement.reqNumber}
        </span>
        {!isOverlay && (
          <div className="flex items-center gap-2">
            {requirement.returnCount > 0 && (
              <span className="flex items-center gap-1 text-orange-600 text-xs font-bold bg-orange-50 px-2 py-0.5 rounded-full">
                <Undo2 size={12} />
                {requirement.returnCount}
              </span>
            )}
            <button
              onClick={(e) => {
                e.stopPropagation();
                window.open(`/requirements/${requirement.id}`, '_blank');
              }}
              className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
              title="Open in new tab"
            >
              <ExternalLink size={14} className="text-gray-400" />
            </button>
          </div>
        )}
      </div>

      {/* Title */}
      <h4 className="font-semibold text-gray-900 text-base mb-3 leading-snug group-hover:text-blue-600 transition-colors">
        {requirement.title}
      </h4>

      {/* Priority badge and AI indicator */}
      <div className="flex items-center gap-2">
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${getPriorityBadge(requirement.priority)}`}>
          {requirement.priority.toUpperCase()}
        </span>

        {requirement.aiSuggestions && (
          <span className="p-1.5 bg-purple-100 rounded-xl">
            <Sparkles size={14} className="text-purple-600" />
          </span>
        )}
      </div>
    </>
  );

  if (isOverlay) {
    return (
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-4 shadow-xl border border-gray-200/60 w-[300px]">
        {cardContent}
      </div>
    );
  }

  return (
    <>
      <div
        ref={setNodeRef}
        style={style}
        {...attributes}
        {...listeners}
        onDoubleClick={handleDoubleClick}
        className="bg-white/80 backdrop-blur-xl rounded-2xl p-4 shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-all border border-gray-200/60 group relative cursor-grab active:cursor-grabbing"
      >
        {cardContent}
      </div>

      {showDetail && (
        <RequirementDetail
          requirement={requirement}
          onClose={() => setShowDetail(false)}
        />
      )}
    </>
  );
}
