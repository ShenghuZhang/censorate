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
      <div className="flex flex-col sm:flex-row gap-3 mb-5 items-start sm:items-center justify-between">
        <div className="flex-1 w-full sm:w-auto">
          <div className="relative">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-muted" />
            <input
              type="text"
              placeholder="Search members..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full sm:w-72 pl-10 pr-3.5 py-2.5 bg-surface-soft border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-text-primary text-sm"
            />
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Filter */}
          <div className="flex items-center gap-1.5 bg-surface-soft rounded-lg p-1">
            {(['all', 'human', 'ai'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={clsx(
                  'px-3.5 py-2 rounded-lg text-sm font-medium transition-all',
                  filterType === type
                    ? 'bg-white text-text-primary shadow-soft'
                    : 'text-text-secondary hover:text-text-primary'
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
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all font-medium text-sm shadow-soft hover:shadow-medium"
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
          <div className="animate-spin w-7 h-7 border-2 border-border rounded-full border-t-primary" />
        </div>
      ) : filteredMembers.length === 0 ? (
        <div className="bg-white rounded-lg shadow-soft border border-border p-10 text-center">
          <div className="w-14 h-14 bg-surface-soft rounded-2xl flex items-center justify-center mx-auto mb-3">
            <Filter size={28} className="text-text-muted" />
          </div>
          <h3 className="text-base font-semibold text-text-primary mb-2">
            No members found
          </h3>
          <p className="text-text-muted text-sm">
            {searchQuery || filterType !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Start by adding team members or AI agents'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
