'use client';

import { useState, useEffect } from 'react';
import { X, Calendar, Users, Brain, StickyNote } from 'lucide-react';
import { useTeamStore, type TeamMember, type AIAgent } from '@/app/stores/teamStore';
import { useProjectStore } from '@/app/stores/projectStore';
import RichTextEditor from '../common/RichTextEditor';

interface TransitionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (data: {
    assignedTo?: string;
    expectedCompletionAt?: string;
    note?: string;
  }) => void;
  fromStatus: string;
  toStatus: string;
  requirementTitle: string;
}

export default function TransitionDialog({
  isOpen,
  onClose,
  onConfirm,
  fromStatus,
  toStatus,
  requirementTitle
}: TransitionDialogProps) {
  const [selectedAssignee, setSelectedAssignee] = useState<string | undefined>();
  const [selectedDate, setSelectedDate] = useState<string | undefined>();
  const [note, setNote] = useState('');
  const { members, aiAgents, fetchMembers } = useTeamStore();
  const { currentProject } = useProjectStore();

  useEffect(() => {
    if (isOpen && currentProject) {
      fetchMembers(currentProject.id);
    }
  }, [isOpen, currentProject, fetchMembers]);

  useEffect(() => {
    // Reset form when opening
    if (isOpen) {
      const allAssignees = [...members, ...aiAgents];
      setSelectedAssignee(allAssignees.length > 0 ? allAssignees[0].id : undefined);
      setSelectedDate(undefined);
      setNote('');
    }
  }, [isOpen, members, aiAgents]);

  if (!isOpen) return null;

  const allAssignees = [...members, ...aiAgents];

  const handleConfirm = () => {
    const allAssignees = [...members, ...aiAgents];
    const selectedAssigneeObj = allAssignees.find(a => a.id === selectedAssignee);

    onConfirm({
      assignedTo: selectedAssignee,
      assignedToName: selectedAssigneeObj?.nickname || selectedAssigneeObj?.name,
      expectedCompletionAt: selectedDate,
      note: note || undefined
    });
    onClose();
  };

  const formatStatus = (status: string) => {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              Move to {formatStatus(toStatus)}
            </h2>
            <p className="text-sm text-gray-500 mt-1">{requirementTitle}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Status transition info */}
          <div className="flex items-center gap-3 text-sm text-gray-500 bg-gray-50 p-3 rounded-lg">
            <span className="font-medium text-gray-700">{formatStatus(fromStatus)}</span>
            <span className="text-gray-400">→</span>
            <span className="font-medium text-gray-900">{formatStatus(toStatus)}</span>
          </div>

          {/* Assignee */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
              <Users size={16} />
              Assign to
            </label>
            <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
              {allAssignees.map(assignee => (
                <button
                  key={assignee.id}
                  onClick={() => setSelectedAssignee(assignee.id)}
                  className={`flex items-center gap-3 p-3 rounded-xl border-2 transition-all text-left ${
                    selectedAssignee === assignee.id
                      ? 'border-gray-800 bg-gray-50'
                      : 'border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    assignee.type === 'ai' ? 'bg-gradient-to-br from-purple-500 to-blue-500' : 'bg-gray-200'
                  }`}>
                    {assignee.type === 'ai' ? (
                      <Brain size={20} className="text-white" />
                    ) : (
                      <span className="text-gray-600 font-medium">
                        {assignee.nickname?.[0]?.toUpperCase() || '?'}
                      </span>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 flex items-center gap-2">
                      {assignee.nickname}
                      {assignee.type === 'ai' && <span className="text-xs text-purple-600">(AI)</span>}
                    </p>
                    <p className="text-sm text-gray-500">{assignee.role?.replace('_', ' ')}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Expected Date */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
              <Calendar size={16} />
              Expected completion date (optional)
            </label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value || undefined)}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-gray-300 focus:border-gray-400"
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          {/* Note */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
              <StickyNote size={16} />
              Note (optional)
            </label>
            <RichTextEditor
              value={note}
              onChange={setNote}
              placeholder="Add a note about this transition..."
              minHeight="100px"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100">
          <button
            onClick={onClose}
            className="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            className="px-5 py-2.5 bg-gray-800 text-white rounded-xl hover:bg-gray-700 transition-colors"
          >
            Move Card
          </button>
        </div>
      </div>
    </div>
  );
}
