'use client';

import { useRef } from 'react';
import { Plus, MoreHorizontal, Circle, Clock, CheckCircle2 } from 'lucide-react';
import { useDroppable } from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import RequirementCard from './RequirementCard';
import { Requirement } from '@/app/stores/requirementStore';

interface SwimlaneProps {
  lane: {
    id: string;
    title: string;
    color: string;
    badgeColor: string;
  };
  requirements: Requirement[];
}

const getLaneIcon = (title: string) => {
  switch (title.toLowerCase()) {
    case 'todo':
      return <Clock size={18} className="text-white" />;
    case 'in review':
      return <CheckCircle2 size={18} className="text-white" />;
    case 'done':
      return <CheckCircle2 size={18} className="text-white" />;
    default:
      return <Circle size={18} className="text-white" />;
  }
};

export default function Swimlane({ lane, requirements }: SwimlaneProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: lane.id,
  });

  const requirementIds = requirements.map(req => req.id);

  return (
    <div
      ref={setNodeRef}
      className={`min-w-[300px] max-w-[300px] rounded-2xl ${lane.color} transition-all flex flex-col`}
    >
      {/* Lane header - fixed, won't shrink */}
      <div className="px-4 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-lg text-sm font-semibold flex items-center gap-1.5 ${lane.badgeColor}`}>
              {getLaneIcon(lane.title)}
              {lane.title}
            </span>
            <span className="text-gray-500 font-medium text-lg">
              {requirements.length}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button className="p-1.5 hover:bg-white/70 rounded-lg transition-colors">
              <MoreHorizontal size={18} className="text-gray-400" />
            </button>
            <button className="p-1.5 hover:bg-white/70 rounded-lg transition-colors">
              <Plus size={18} className="text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Cards container - this will scroll if content overflows */}
      <SortableContext
        items={requirementIds}
        strategy={verticalListSortingStrategy}
      >
        <div
          className={`px-3 pb-3 space-y-3 flex-1 overflow-y-auto rounded-b-2xl transition-all ${
            isOver ? 'ring-2 ring-blue-400 ring-inset bg-blue-50/30' : ''
          }`}
        >
          {requirements.length === 0 ? (
            <div className="flex items-center justify-center py-12 flex-shrink-0">
              <p className="text-gray-400 text-sm font-medium">No issues</p>
            </div>
          ) : (
            requirements.map(requirement => (
              <RequirementCard
                key={requirement.id}
                requirement={requirement}
              />
            ))
          )}
        </div>
      </SortableContext>
    </div>
  );
}
