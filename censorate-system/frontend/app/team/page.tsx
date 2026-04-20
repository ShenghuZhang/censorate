'use client';

import { useState, useEffect } from 'react';
import { useTeamStore } from '@/app/stores/teamStore';
import AgentCard from '@/app/components/team/AgentCard';
import AddAgentDialog from '@/app/components/team/AddAgentDialog';
import Layout from '@/app/components/layout/Layout';

export default function TeamPage() {
  const { members, aiAgents, isLoading, fetchMembers } = useTeamStore();
  const [showAddAgent, setShowAddAgent] = useState(false);
  const projectId = '58d22de7-ddfd-4996-be3d-48e29599604d';

  useEffect(() => {
    fetchMembers(projectId);
  }, [fetchMembers]);

  const handleAddAgent = async (agentData: any) => {
    console.log('Adding agent:', agentData);
    setShowAddAgent(false);
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Team Members</h1>
            <p className="text-gray-600 mt-2">Manage your team and AI agents</p>
          </div>
          <button
            onClick={() => setShowAddAgent(true)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add AI Agent
          </button>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-blue-600 rounded-full border-t-transparent" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {aiAgents.map(agent => (
              <AgentCard
                key={agent.id}
                agent={agent}
              />
            ))}
          </div>
        )}

        <AddAgentDialog
          isOpen={showAddAgent}
          onClose={() => setShowAddAgent(false)}
          existingRoles={aiAgents.map(a => a.role)}
        />
      </div>
    </Layout>
  );
}
