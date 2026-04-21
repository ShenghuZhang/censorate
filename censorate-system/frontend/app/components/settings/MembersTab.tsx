'use client';

import { useState, useEffect } from 'react';
import { useTeamStore, TeamMember, AIAgent } from '@/app/stores/teamStore';
import { useProjectStore } from '@/app/stores/projectStore';
import MemberCard from './MemberCard';
import AddAgentDialog from '@/app/components/team/AddAgentDialog';
import { Plus, Search, Filter, UserPlus, Brain } from 'lucide-react';
import { clsx } from 'clsx';

export default function MembersTab() {
  const { currentProject } = useProjectStore();
  const { members, aiAgents, isLoading, fetchMembers, removeMember, removeAgent } = useTeamStore();
  const [showAddAgent, setShowAddAgent] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'human' | 'ai'>('all');
  const [showAddMenu, setShowAddMenu] = useState(false);

  useEffect(() => {
    if (currentProject) {
      fetchMembers(currentProject.id);
    }
  }, [currentProject, fetchMembers]);

  const allMembers = [...members, ...aiAgents];

  const filteredMembers = allMembers.filter(member => {
    const matchesSearch =
      member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.nickname.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.role.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesType =
      filterType === 'all' ||
      (filterType === 'human' && member.type === 'human') ||
      (filterType === 'ai' && member.type === 'ai');

    return matchesSearch && matchesType;
  });

  const handleRemoveMember = (id: string) => {
    const member = members.find(m => m.id === id);
    const agent = aiAgents.find(a => a.id === id);

    if (member) {
      removeMember(id);
    } else if (agent) {
      removeAgent(id);
    }
  };

  const handleAddHuman = () => {
    setShowAddMenu(false);
    // TODO: Implement add human member dialog
    alert('Add Human Member - Coming Soon');
  };

  return (
    <div>
      {/* Header with search and filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6 items-start sm:items-center justify-between">
        <div className="flex-1 w-full sm:w-auto">
          <div className="relative">
            <Search size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search members..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full sm:w-72 pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-300 focus:border-slate-400 outline-none transition-all duration-200 text-slate-700 text-sm shadow-sm"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Filter */}
          <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-xl p-1 shadow-sm">
            {(['all', 'human', 'ai'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={clsx(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                  filterType === type
                    ? 'bg-white text-slate-700 shadow-md'
                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50/60'
                )}
              >
                {type === 'all' ? 'All' : type === 'human' ? 'Humans' : 'AI Agents'}
              </button>
            ))}
          </div>

          {/* Add button */}
          <div className="relative">
            <button
              onClick={() => setShowAddMenu(!showAddMenu)}
              className="inline-flex items-center gap-2 px-5 py-3 bg-slate-600 text-white rounded-xl hover:bg-slate-700 transition-all duration-200 font-medium text-sm shadow-md hover:shadow-lg"
            >
              <Plus size={16} strokeWidth={2} />
              Add
            </button>

            {showAddMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowAddMenu(false)}
                />
                <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-lg border border-border shadow-medium z-20 py-1">
                  <button
                    onClick={handleAddHuman}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-text-secondary hover:bg-surface-soft transition-colors"
                  >
                    <UserPlus size={16} />
                    Add Human Member
                  </button>
                  <button
                    onClick={() => {
                      setShowAddMenu(false);
                      setShowAddAgent(true);
                    }}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-text-secondary hover:bg-surface-soft transition-colors"
                  >
                    <Brain size={16} />
                    Add AI Agent
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Members Grid */}
      {isLoading ? (
        <div className="flex justify-center py-14">
          <div className="animate-spin w-8 h-8 border-2 border-slate-200 rounded-full border-t-slate-500" />
        </div>
      ) : filteredMembers.length === 0 ? (
        <div className="bg-slate-50/70 border border-slate-200/60 rounded-2xl p-12 text-center shadow-sm">
          <div className="w-16 h-16 bg-slate-100 border border-slate-200/50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
            <Filter size={32} className="text-slate-400" />
          </div>
          <h3 className="text-lg font-medium text-slate-700 mb-2">
            No members found
          </h3>
          <p className="text-slate-500 text-sm">
            {searchQuery || filterType !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Start by adding team members or AI agents'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredMembers.map((member) => (
            <MemberCard
              key={member.id}
              member={member}
              onRemove={handleRemoveMember}
            />
          ))}
        </div>
      )}

      {/* Add Agent Dialog */}
      <AddAgentDialog
        isOpen={showAddAgent}
        onClose={() => setShowAddAgent(false)}
        existingRoles={aiAgents.map(a => a.role)}
      />
    </div>
  );
}
