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
import { useProjectStore } from '@/app/stores/projectStore';
import { useAuthStore } from '@/app/stores/authStore';
import { Plus, MoreHorizontal, Filter, List, Layout } from 'lucide-react';
import Swimlane from './Swimlane';
import RequirementCard from './RequirementCard';
import TransitionDialog from './TransitionDialog';

// Default swimlane configuration
const DEFAULT_SWIMLANES = ['Backlog', 'Todo', 'In Review', 'Done'];

// Convert display name to valid ID (snake_case)
function slugifyLaneName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '_')
    .replace(/^_|_$/g, '')
    || `lane_${Date.now()}`;
}

// Get lane colors based on index
function getLaneColors(index: number, total: number) {
  if (index === 0) {
    return { color: 'bg-gray-50/50', badgeColor: 'bg-gray-600 text-white' };
  }
  if (index === total - 1) {
    return { color: 'bg-green-50/50', badgeColor: 'bg-green-600 text-white' };
  }
  const middleColors = [
    { color: 'bg-blue-50/50', badgeColor: 'bg-blue-600 text-white' },
    { color: 'bg-amber-50/50', badgeColor: 'bg-amber-600 text-white' },
    { color: 'bg-purple-50/50', badgeColor: 'bg-purple-600 text-white' },
    { color: 'bg-pink-50/50', badgeColor: 'bg-pink-600 text-white' },
  ];
  return middleColors[(index - 1) % middleColors.length];
}

export default function KanbanBoard() {
  const { requirements, transitionRequirement, transitionWithData } = useRequirementStore();
  const { currentProject } = useProjectStore();
  const [activeTab, setActiveTab] = useState<'all' | 'members' | 'agents'>('all');
  const [viewMode, setViewMode] = useState<'list' | 'board'>('board');
  const [activeId, setActiveId] = useState<string | null>(null);
  const [showTransitionDialog, setShowTransitionDialog] = useState(false);
  const [pendingTransition, setPendingTransition] = useState<{
    requirementId: string;
    toStatus: string;
    fromStatus: string;
    title: string;
  } | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(KeyboardSensor)
  );

  // Get swimlane configuration from project or use default
  const swimlaneNames = currentProject?.settings?.swimlanes || DEFAULT_SWIMLANES;

  // Generate swimlane objects dynamically
  const SWIMLANES = swimlaneNames.map((name, index) => ({
    id: slugifyLaneName(name),
    title: name,
    ...getLaneColors(index, swimlaneNames.length),
  }));

  // Get valid lane IDs
  const validLaneIds = SWIMLANES.map(l => l.id);

  // Get valid status for a requirement (falls back to first lane if invalid)
  const getValidStatus = (status: string) => {
    return validLaneIds.includes(status) ? status : validLaneIds[0];
  };

  const getRequirementsByStatus = (status: string) => {
    return requirements.filter(req => getValidStatus(req.status) === status);
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
        // 判断是否为向前移动
        const swimlanes = currentProject?.settings?.swimlanes || DEFAULT_SWIMLANES;
        const laneIds = swimlanes.map(s => slugifyLaneName(s));
        const fromIndex = laneIds.indexOf(req.status);
        const toIndex = laneIds.indexOf(overId);
        const isForward = toIndex > fromIndex;

        if (isForward) {
          // 向前移动：显示对话框
          setPendingTransition({
            requirementId: activeCardId,
            toStatus: overId,
            fromStatus: req.status,
            title: req.title
          });
          setShowTransitionDialog(true);
        } else {
          // 向后移动：直接移动，后端会自动恢复负责人
          await transitionRequirement(activeCardId, overId, false);
        }
      }
      setActiveId(null);
      return;
    }

    // Check if we're dropping over another card (get its status)
    const overReq = requirements.find(r => r.id === overId);
    if (overReq) {
      const req = requirements.find(r => r.id === activeCardId);
      if (req && req.status !== overReq.status) {
        // 判断是否为向前移动
        const swimlanes = currentProject?.settings?.swimlanes || DEFAULT_SWIMLANES;
        const laneIds = swimlanes.map(s => slugifyLaneName(s));
        const fromIndex = laneIds.indexOf(req.status);
        const toIndex = laneIds.indexOf(overReq.status);
        const isForward = toIndex > fromIndex;

        if (isForward) {
          // 向前移动：显示对话框
          setPendingTransition({
            requirementId: activeCardId,
            toStatus: overReq.status,
            fromStatus: req.status,
            title: req.title
          });
          setShowTransitionDialog(true);
        } else {
          // 向后移动：直接移动，后端会自动恢复负责人
          await transitionRequirement(activeCardId, overReq.status, false);
        }
      }
    }
    setActiveId(null);
  };

  const handleTransitionConfirm = async (data: {
    assignedTo?: string;
    assignedToName?: string;
    expectedCompletionAt?: string;
    note?: string;
  }) => {
    if (!pendingTransition) return;

    const { user } = useAuthStore.getState();

    await transitionWithData(pendingTransition.requirementId, {
      toStatus: pendingTransition.toStatus,
      assignedTo: data.assignedTo,
      assignedToName: data.assignedToName,
      expectedCompletionAt: data.expectedCompletionAt,
      note: data.note,
      changedBy: user?.id,
      changedByName: user?.name || "你"
    });

    setPendingTransition(null);
  };

  const activeRequirement = activeId ? requirements.find(r => r.id === activeId) : null;

  return (
    <>
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

      {/* Transition Dialog */}
      {showTransitionDialog && pendingTransition && (
        <TransitionDialog
          isOpen={showTransitionDialog}
          onClose={() => {
            setShowTransitionDialog(false);
            setPendingTransition(null);
          }}
          onConfirm={handleTransitionConfirm}
          fromStatus={pendingTransition.fromStatus}
          toStatus={pendingTransition.toStatus}
          requirementTitle={pendingTransition.title}
        />
      )}
    </>
  );
}
