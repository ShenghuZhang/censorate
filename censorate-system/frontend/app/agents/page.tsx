'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Layout from '@/app/components/layout/Layout';
import { Bot, Plus, RefreshCw, MessageSquare, Trash2, Edit2, Settings, Activity } from 'lucide-react';
import { remoteAgentsAPI, type RemoteAgent } from '@/lib/api/remoteAgents';
import { useProjectStore } from '@/app/stores/projectStore';
import { useAuth } from '@/app/hooks/useAuth';
import { clsx } from 'clsx';

type AgentStatus = 'online' | 'offline' | 'error';

const HealthStatusBadge = ({ status }: { status: AgentStatus }) => {
  const statusConfig = {
    online: { bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500', label: 'Online' },
    offline: { bg: 'bg-gray-100', text: 'text-gray-600', dot: 'bg-gray-400', label: 'Offline' },
    error: { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500', label: 'Error' },
  };

  const config = statusConfig[status] || statusConfig.offline;

  return (
    <span className={clsx('inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-lg', config.bg, config.text)}>
      <span className={clsx('w-2 h-2 rounded-full animate-pulse', config.dot)} />
      {config.label}
    </span>
  );
};

export default function AgentsPage() {
  const [agents, setAgents] = useState<RemoteAgent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);
  const [showChat, setShowChat] = useState<RemoteAgent | null>(null);
  const [showEdit, setShowEdit] = useState<RemoteAgent | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'agent'; content: string; timestamp: string }>>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatThreadId, setChatThreadId] = useState<string | undefined>();
  const { currentProject } = useProjectStore();
  const { user } = useAuth();
  const [isSending, setIsSending] = useState(false);
  const [registerForm, setRegisterForm] = useState({
    name: '',
    agentType: 'custom' as const,
    endpointUrl: '',
    healthCheckPath: '/health',
    apiKey: '',
    healthCheckInterval: 30,
    description: '',
    capabilities: '' as string,
  });

  const [editForm, setEditForm] = useState({
    name: '',
    agentType: 'custom' as const,
    endpointUrl: '',
    healthCheckPath: '/health',
    apiKey: '',
    healthCheckInterval: 30,
    description: '',
    capabilities: '',
  });

  const loadAgents = useCallback(async () => {
    try {
      const data = await remoteAgentsAPI.listAgents();
      setAgents(data);
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  // Auto-refresh health status periodically
  useEffect(() => {
    const interval = setInterval(() => {
      loadAgents();
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [loadAgents]);

  const handleCheckHealth = async (agentId: string) => {
    try {
      await remoteAgentsAPI.checkHealth(agentId);
      await loadAgents();
    } catch (error) {
      console.error('Failed to check health:', error);
    }
  };

  const handleRegister = async () => {
    try {
      await remoteAgentsAPI.registerAgent({
        ...registerForm,
        capabilities: registerForm.capabilities.split(',').map(s => s.trim()).filter(Boolean),
      });
      setShowRegister(false);
      setRegisterForm({
        name: '',
        agentType: 'custom',
        endpointUrl: '',
        healthCheckPath: '/health',
        apiKey: '',
        healthCheckInterval: 30,
        description: '',
        capabilities: '',
      });
      await loadAgents();
    } catch (error) {
      console.error('Failed to register agent:', error);
      alert(error instanceof Error ? error.message : 'Failed to register agent');
    }
  };

  const handleUnregister = async (agentId: string) => {
    if (!confirm('Are you sure you want to unregister this agent?')) return;

    try {
      await remoteAgentsAPI.unregisterAgent(agentId);
      await loadAgents();
    } catch (error) {
      console.error('Failed to unregister agent:', error);
    }
  };

  const handleEdit = async () => {
    if (!showEdit) return;

    try {
      await remoteAgentsAPI.updateAgent(showEdit.id, {
        ...editForm,
        capabilities: editForm.capabilities.split(',').map(s => s.trim()).filter(Boolean),
      });
      setShowEdit(null);
      await loadAgents();
    } catch (error) {
      console.error('Failed to update agent:', error);
      alert(error instanceof Error ? error.message : 'Failed to update agent');
    }
  };

  // Populate edit form when showEdit changes
  useEffect(() => {
    if (showEdit) {
      setEditForm({
        name: showEdit.name || '',
        agentType: showEdit.agentType || 'custom',
        endpointUrl: showEdit.endpointUrl || '',
        healthCheckPath: showEdit.healthCheckPath || '/health',
        apiKey: '', // Don't populate API key for security
        healthCheckInterval: showEdit.healthCheckInterval || 30,
        description: showEdit.description || '',
        capabilities: (showEdit.capabilities || []).join(', '),
      });
    }
  }, [showEdit]);

  const handleSendMessage = async () => {
    if (!showChat || !chatInput.trim() || isSending) return;

    const message = chatInput.trim();
    setChatInput('');
    setIsSending(true);

    // Add user message
    const userMessage = {
      role: 'user' as const,
      content: message,
      timestamp: new Date().toISOString(),
    };
    setChatMessages(prev => [...prev, userMessage]);

    try {
      // Use project ID if available, otherwise use user ID for session continuity
      const sessionProjectId = currentProject?.id;
      const sessionUserId = user?.id;

      const response = await remoteAgentsAPI.sendMessage(showChat.id, {
        message,
        threadId: chatThreadId,
        projectId: sessionProjectId || sessionUserId,
      });

      setChatThreadId(response.threadId);

      // Add agent message
      const agentMessage = {
        role: 'agent' as const,
        content: response.response,
        timestamp: response.timestamp,
      };
      setChatMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <Bot size={24} className="text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Agents</h1>
          </div>
          <p className="text-gray-500 text-sm">
            Register and manage remote AI agents
          </p>
        </div>

        {/* Toolbar */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2.5">
            <button
              onClick={loadAgents}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all font-medium text-sm"
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>

          <button
            onClick={() => setShowRegister(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-medium text-sm"
          >
            <Plus size={16} />
            Register Agent
          </button>
        </div>

        {/* Agents Grid */}
        {isLoading ? (
          <div className="flex justify-center py-14">
            <div className="animate-spin w-7 h-7 border-2 border-gray-200 rounded-full border-t-blue-600" />
          </div>
        ) : agents.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-10 text-center">
            <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
              <Bot size={28} className="text-gray-400" />
            </div>
            <h3 className="text-base font-semibold text-gray-900 mb-2">
              No agents registered
            </h3>
            <p className="text-gray-500 text-sm">
              Start by registering a remote agent
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white shadow-sm">
                      <Bot size={24} />
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">{agent.name}</h3>
                      <p className="text-xs text-gray-500">{agent.agentType}</p>
                      <div className="mt-2">
                        <HealthStatusBadge status={agent.status} />
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleCheckHealth(agent.id)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      title="Check Health"
                    >
                      <Activity size={16} className="text-gray-500" />
                    </button>
                    <button
                      onClick={() => setShowEdit(agent)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <Edit2 size={16} className="text-gray-500" />
                    </button>
                    <button
                      onClick={() => setShowChat(agent)}
                      disabled={agent.status !== 'online'}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
                      title="Chat"
                    >
                      <MessageSquare size={16} className="text-gray-500" />
                    </button>
                    <button
                      onClick={() => handleUnregister(agent.id)}
                      className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                      title="Unregister"
                    >
                      <Trash2 size={16} className="text-gray-500 hover:text-red-600" />
                    </button>
                  </div>
                </div>

                {agent.description && (
                  <p className="text-sm text-gray-500 mt-3 line-clamp-2">
                    {agent.description}
                  </p>
                )}

                {agent.capabilities.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {agent.capabilities.map((cap, idx) => (
                      <span
                        key={idx}
                        className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-md"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                )}

                <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {agent.lastHealthCheck
                      ? `Last check: ${new Date(agent.lastHealthCheck).toLocaleTimeString()}`
                      : 'No health check yet'}
                  </span>
                  <span className="text-xs text-gray-500 font-mono">
                    {agent.endpointUrl}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Register Dialog */}
        {showRegister && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setShowRegister(false)} />
            <div className="relative bg-white rounded-xl shadow-lg max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Register Agent</h2>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Name</label>
                    <input
                      type="text"
                      value={registerForm.name}
                      onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                      placeholder="My Agent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Type</label>
                    <select
                      value={registerForm.agentType}
                      onChange={(e) => setRegisterForm({ ...registerForm, agentType: e.target.value as any })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    >
                      <option value="hermes">Hermes</option>
                      <option value="openclaw">OpenClaw</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Endpoint URL</label>
                  <input
                    type="text"
                    value={registerForm.endpointUrl}
                    onChange={(e) => setRegisterForm({ ...registerForm, endpointUrl: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    placeholder="http://localhost:8000"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Health Check Path</label>
                    <input
                      type="text"
                      value={registerForm.healthCheckPath}
                      onChange={(e) => setRegisterForm({ ...registerForm, healthCheckPath: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                      placeholder="/health"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Check Interval (sec)</label>
                    <input
                      type="number"
                      value={registerForm.healthCheckInterval}
                      onChange={(e) => setRegisterForm({ ...registerForm, healthCheckInterval: parseInt(e.target.value) || 30 })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                      min="10"
                      max="300"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">API Key (optional)</label>
                  <input
                    type="password"
                    value={registerForm.apiKey}
                    onChange={(e) => setRegisterForm({ ...registerForm, apiKey: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    placeholder="sk-..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
                  <textarea
                    value={registerForm.description}
                    onChange={(e) => setRegisterForm({ ...registerForm, description: e.target.value })}
                    rows={2}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm resize-none"
                    placeholder="Agent description..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Capabilities (comma-separated)</label>
                  <input
                    type="text"
                    value={registerForm.capabilities}
                    onChange={(e) => setRegisterForm({ ...registerForm, capabilities: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    placeholder="analysis, coding, review"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowRegister(false)}
                  className="px-4 py-2.5 text-gray-600 hover:text-gray-900 font-medium text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleRegister}
                  className="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm"
                >
                  Register
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Edit Dialog */}
        {showEdit && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setShowEdit(null)} />
            <div className="relative bg-white rounded-xl shadow-lg max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Edit Agent</h2>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Name</label>
                    <input
                      type="text"
                      value={editForm.name}
                      onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                      placeholder="My Agent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Type</label>
                    <select
                      value={editForm.agentType}
                      onChange={(e) => setEditForm({ ...editForm, agentType: e.target.value as any })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    >
                      <option value="hermes">Hermes</option>
                      <option value="openclaw">OpenClaw</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Endpoint URL</label>
                  <input
                    type="text"
                    value={editForm.endpointUrl}
                    onChange={(e) => setEditForm({ ...editForm, endpointUrl: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    placeholder="http://localhost:8000"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Health Check Path</label>
                    <input
                      type="text"
                      value={editForm.healthCheckPath}
                      onChange={(e) => setEditForm({ ...editForm, healthCheckPath: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                      placeholder="/health"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Check Interval (sec)</label>
                    <input
                      type="number"
                      value={editForm.healthCheckInterval}
                      onChange={(e) => setEditForm({ ...editForm, healthCheckInterval: parseInt(e.target.value) || 30 })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                      min="10"
                      max="300"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">API Key (leave blank to keep unchanged)</label>
                  <input
                    type="password"
                    value={editForm.apiKey}
                    onChange={(e) => setEditForm({ ...editForm, apiKey: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    placeholder="sk-..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
                  <textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    rows={2}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm resize-none"
                    placeholder="Agent description..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Capabilities (comma-separated)</label>
                  <input
                    type="text"
                    value={editForm.capabilities}
                    onChange={(e) => setEditForm({ ...editForm, capabilities: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    placeholder="analysis, coding, review"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowEdit(null)}
                  className="px-4 py-2.5 text-gray-600 hover:text-gray-900 font-medium text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleEdit}
                  className="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Chat Dialog */}
        {showChat && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setShowChat(null)} />
            <div className="relative bg-white rounded-xl shadow-lg max-w-2xl w-full h-[600px] flex flex-col">
              <div className="p-4 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                      <Bot size={20} className="text-white" />
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">{showChat.name}</h3>
                      <HealthStatusBadge status={showChat.status} />
                    </div>
                  </div>
                <button
                  onClick={() => setShowChat(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              {currentProject ? (
                <div className="mt-3 px-3 py-2 bg-blue-50 rounded-lg text-sm">
                  <span className="text-blue-600 font-medium">Project:</span>
                  <span className="text-blue-800 ml-2">{currentProject.name}</span>
                  <span className="text-blue-400 ml-2 text-xs">(Session linked to project)</span>
                </div>
              ) : user ? (
                <div className="mt-3 px-3 py-2 bg-purple-50 rounded-lg text-sm">
                  <span className="text-purple-600 font-medium">User:</span>
                  <span className="text-purple-800 ml-2">{user.name}</span>
                  <span className="text-purple-400 ml-2 text-xs">(Session linked to user)</span>
                </div>
              ) : null}
            </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {chatMessages.length === 0 ? (
                  <div className="text-center py-10">
                    <MessageSquare size={32} className="mx-auto mb-2 text-gray-300" />
                    <p className="text-gray-500 text-sm">Start a conversation with {showChat.name}</p>
                  </div>
                ) : (
                  chatMessages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={clsx(
                        'max-w-[80%] p-3 rounded-lg',
                        msg.role === 'user'
                          ? 'ml-auto bg-blue-600 text-white'
                          : 'mr-auto bg-gray-100 text-gray-900'
                      )}
                    >
                      <p className="text-sm">{msg.content}</p>
                      <p className={clsx(
                        'text-xs mt-1 opacity-70',
                        msg.role === 'user' ? 'text-right' : 'text-left'
                      )}>
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  ))
                )}
                {isSending && (
                  <div className="mr-auto bg-gray-100 text-gray-900 max-w-[80%] p-3 rounded-lg">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                )}
              </div>

              <div className="p-4 border-t border-gray-100">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type a message..."
                    className="flex-1 px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    disabled={isSending}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!chatInput.trim() || isSending}
                    className="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium text-sm"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
