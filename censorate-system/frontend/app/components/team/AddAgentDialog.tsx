'use client';

import { useState, useEffect } from 'react';
import { useTeamStore } from '@/app/stores/teamStore';
import { remoteAgentsAPI, RemoteAgent } from '@/lib/api/remoteAgents';
import { X, AlertCircle } from 'lucide-react';

interface AddAgentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  existingRoles: string[];
}

export default function AddAgentDialog({ isOpen, onClose, existingRoles }: AddAgentDialogProps) {
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [registeredAgents, setRegisteredAgents] = useState<RemoteAgent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [nickname, setNickname] = useState('');
  const [role, setRole] = useState('');
  const [memoryEnabled, setMemoryEnabled] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const { addAgent, aiAgents } = useTeamStore();
  const projectId = '3cfd0fdd-7e9c-42fa-9df1-a663ce735cda';

  const availableRoles = [
    'analysis_agent',
    'design_agent',
    'development_agent',
    'testing_agent',
    'review_agent'
  ].filter(r => !existingRoles.includes(r));

  // Check if we already have an agent
  const hasExistingAgent = aiAgents.length >= 1;

  // Load registered agents when dialog opens
  useEffect(() => {
    if (isOpen) {
      setErrorMessage('');
      loadRegisteredAgents();
    }
  }, [isOpen]);

  const loadRegisteredAgents = async () => {
    setIsLoading(true);
    try {
      const agents = await remoteAgentsAPI.listAgents();
      setRegisteredAgents(agents);
    } catch (error) {
      console.error('Failed to load registered agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSelectedAgent = () => {
    return registeredAgents.find(a => a.id === selectedAgentId);
  };

  // Auto-fill role based on agent type when agent is selected
  useEffect(() => {
    const agent = getSelectedAgent();
    if (agent) {
      // Map agent type to role
      const agentTypeToRole: Record<string, string> = {
        'hermes': 'analysis_agent',
        'openclaw': 'development_agent',
        'custom': 'review_agent'
      };
      const suggestedRole = agentTypeToRole[agent.agentType] || availableRoles[0] || 'review_agent';
      if (availableRoles.includes(suggestedRole)) {
        setRole(suggestedRole);
      } else if (availableRoles.length > 0) {
        setRole(availableRoles[0]);
      }
    }
  }, [selectedAgentId, registeredAgents, availableRoles]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    const agent = getSelectedAgent();
    if (!agent) return;

    try {
      await addAgent(projectId, {
        name: agent.name,
        nickname: nickname || agent.name,
        role,
        skills: agent.capabilities || [],
        memoryEnabled,
        agentType: agent.agentType,
        deepagentConfig: {
          remoteAgentId: agent.id,
          endpointUrl: agent.endpointUrl,
          ...agent.config
        },
        status: 'active'
      });
      onClose();
    } catch (error) {
      console.error('Failed to add agent:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to add agent');
    }
  };

  const resetForm = () => {
    setSelectedAgentId('');
    setNickname('');
    setRole('');
    setMemoryEnabled(true);
    setErrorMessage('');
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  if (!isOpen) return null;

  const selectedAgent = getSelectedAgent();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl w-full max-w-md max-h-[80vh] overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-bold">Add AI Agent</h2>
          <button onClick={handleClose} className="p-2 hover:bg-gray-100 rounded">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto">
          <div className="space-y-4">
            {hasExistingAgent ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <AlertCircle size={32} className="text-amber-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Project already has an AI Agent
                </h3>
                <p className="text-gray-600 mb-4">
                  Each project can only have one AI agent member.
                </p>
                <p className="text-sm text-gray-500">
                  Current Agent: <span className="font-medium">{aiAgents[0]?.name}</span>
                </p>
              </div>
            ) : isLoading ? (
              <div className="text-center py-8">
                <div className="w-6 h-6 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin mx-auto mb-2"></div>
                <p className="text-gray-500">Loading registered agents...</p>
              </div>
            ) : registeredAgents.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No registered agents found</p>
                <p className="text-sm text-gray-400">
                  Go to the <span className="text-blue-600">Agents</span> menu to register agents first
                </p>
              </div>
            ) : (
              <>
                {errorMessage && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm text-red-600">{errorMessage}</p>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Registered Agent
                  </label>
                  <select
                    value={selectedAgentId}
                    onChange={(e) => setSelectedAgentId(e.target.value)}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Choose an agent...</option>
                    {registeredAgents.map(agent => (
                      <option key={agent.id} value={agent.id}>
                        {agent.name} ({agent.agentType}) - {agent.status}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedAgent && (
                  <>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-800 mb-2">{selectedAgent.name}</h4>
                      {selectedAgent.description && (
                        <p className="text-sm text-gray-600 mb-2">{selectedAgent.description}</p>
                      )}
                      <div className="flex flex-wrap gap-1">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          selectedAgent.status === 'online' ? 'bg-green-100 text-green-800' :
                          selectedAgent.status === 'offline' ? 'bg-gray-100 text-gray-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {selectedAgent.status.toUpperCase()}
                        </span>
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                          {selectedAgent.agentType.toUpperCase()}
                        </span>
                      </div>
                      {selectedAgent.capabilities && selectedAgent.capabilities.length > 0 && (
                        <div className="mt-3">
                          <p className="text-xs text-gray-500 mb-1">Capabilities:</p>
                          <div className="flex flex-wrap gap-1">
                            {selectedAgent.capabilities.map((cap, idx) => (
                              <span key={idx} className="px-2 py-0.5 text-xs bg-gray-200 text-gray-700 rounded">
                                {cap}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nickname (optional)
                      </label>
                      <input
                        type="text"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
                        placeholder={`Default: ${selectedAgent.name}`}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Role
                      </label>
                      <select
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        required
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Select role...</option>
                        {availableRoles.map(r => (
                          <option key={r} value={r}>
                            {r.replace('_', ' ').replace(' agent', '').toUpperCase()}
                          </option>
                        ))}
                      </select>
                      {availableRoles.length === 0 && (
                        <p className="text-sm text-red-500 mt-1">
                          All agent roles are already assigned
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        id="memory-enabled"
                        checked={memoryEnabled}
                        onChange={(e) => setMemoryEnabled(e.target.checked)}
                        className="w-5 h-5"
                      />
                      <label htmlFor="memory-enabled" className="text-sm text-gray-700">
                        Enable Long-term Memory
                      </label>
                    </div>
                  </>
                )}

                <div className="flex justify-end gap-3 pt-6">
                  <button
                    type="button"
                    onClick={handleClose}
                    className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  {!hasExistingAgent && registeredAgents.length > 0 && (
                    <button
                      type="submit"
                      disabled={!selectedAgentId || !role}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                    >
                      Add AI Agent
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
