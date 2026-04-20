'use client';

import { useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
} from '@dnd-kit/core';
import { useRequirementStore } from '@/app/stores/requirementStore';
import { Plus, MoreHorizontal, Filter, List, Layout } from 'lucide-react';
import Swimlane from './Swimlane';
import RequirementCard from './RequirementCard';

const SWIMLANES = [
  { id: 'backlog', title: 'Backlog', color: 'bg-gray-50/50', badgeColor: 'bg-gray-600 text-white' },
  { id: 'todo', title: 'Todo', color: 'bg-gray-50/50', badgeColor: 'bg-gray-600 text-white' },
  { id: 'in_review', title: 'In Review', color: 'bg-amber-50/50', badgeColor: 'bg-amber-600 text-white' },
  { id: 'done', title: 'Done', color: 'bg-green-50/50', badgeColor: 'bg-green-600 text-white' },
];

export default function KanbanBoard() {
  const { requirements, transitionRequirement } = useRequirementStore();
  const [activeTab, setActiveTab] = useState<'all' | 'members' | 'agents'>('all');
  const [viewMode, setViewMode] = useState<'list' | 'board'>('board');
  const [activeId, setActiveId] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(KeyboardSensor)
  );

  const getRequirementsByStatus = (status: string) => {
    return requirements.filter(req => req.status === status);
  };

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) {
      setActiveId(null);
      return;
    }

    const activeCardId = active.id as string;
    const overId = over.id as string;

    // Check if we're dropping over a swimlane
    const overLane = SWIMLANES.find(lane => lane.id === overId);
    if (overLane) {
      const req = requirements.find(r => r.id === activeCardId);
      if (req && req.status !== overId) {
        await transitionRequirement(activeCardId, overId, false);
      }
      setActiveId(null);
      return;
    }

    // Check if we're dropping over another card (get its status)
    const overReq = requirements.find(r => r.id === overId);
    if (overReq) {
      const req = requirements.find(r => r.id === activeCardId);
      if (req && req.status !== overReq.status) {
        await transitionRequirement(activeCardId, overReq.status, false);
      }
    }
    setActiveId(null);
  };

  const activeRequirement = activeId ? requirements.find(r => r.id === activeId) : null;

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex flex-col h-[calc(100vh-12rem)]">
        {/* Top controls - sticky, won't scroll */}
        <div className="flex items-center justify-between mb-6 flex-shrink-0">
          {/* View tabs */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-4 py-1.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'all'
                  ? 'bg-gray-100 text-gray-900 border border-gray-300'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setActiveTab('members')}
              className={`px-4 py-1.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'members'
                  ? 'bg-gray-100 text-gray-900 border border-gray-300'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              Members
            </button>
            <button
              onClick={() => setActiveTab('agents')}
              className={`px-4 py-1.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'agents'
                  ? 'bg-gray-100 text-gray-900 border border-gray-300'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              Agents
            </button>
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
              <Filter size={20} className="text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
              <List size={20} className="text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
              <Layout size={20} className="text-gray-600" />
            </button>
          </div>
        </div>

        {/* Kanban board - this scrolls horizontally */}
        <div className="flex gap-4 overflow-x-auto flex-1 pb-4 min-w-0">
          {SWIMLANES.map(lane => (
            <Swimlane
              key={lane.id}
              lane={lane}
              requirements={getRequirementsByStatus(lane.id)}
            />
          ))}
        </div>
      </div>

      <DragOverlay>
        {activeRequirement ? (
          <RequirementCard requirement={activeRequirement} isOverlay />
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
