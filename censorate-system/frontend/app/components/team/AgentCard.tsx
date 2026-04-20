'use client';

import { useState } from 'react';
import { Brain, Settings } from 'lucide-react';
import { AIAgent } from '@/app/stores/teamStore';
import AgentMemoryViewer from './AgentMemoryViewer';

interface AgentCardProps {
  agent: AIAgent;
}

export default function AgentCard({ agent }: AgentCardProps) {
  const [showMemory, setShowMemory] = useState(false);

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'analysis_agent': return 'bg-amber-100 text-amber-800';
      case 'design_agent': return 'bg-blue-100 text-blue-800';
      case 'development_agent': return 'bg-emerald-100 text-emerald-800';
      case 'testing_agent': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow group">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-2xl">
            <Brain size={32} />
          </div>
          <div>
            <h3 className="font-bold text-lg">{agent.nickname}</h3>
            <p className="text-sm text-gray-500">{agent.name}</p>
          </div>
        </div>
        <span className={`text-xs font-bold px-3 py-1 rounded-full ${getRoleBadgeColor(agent.role)}`}>
          {agent.role.replace('_', ' ').replace(' agent', '').toUpperCase()}
        </span>
      </div>

      <div className="space-y-3 mb-6">
        {agent.skills.length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">Skills</p>
            <div className="flex flex-wrap gap-2">
              {agent.skills.map((skill, index) => (
                <span key={index} className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        <div>
          <p className="text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">Memory</p>
          <div className="flex items-center gap-2">
            <span className={`w-3 h-3 rounded-full ${agent.memoryEnabled ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className="text-sm">
              {agent.memoryEnabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center pt-4 border-t">
        <div className="text-xs text-gray-500">
          Joined {new Date(agent.joinedAt).toLocaleDateString()}
        </div>
        <div className="flex gap-2">
          {agent.memoryEnabled && (
            <button
              onClick={() => setShowMemory(true)}
              className="text-sm text-blue-600 hover:underline"
            >
              View Memory
            </button>
          )}
          <button className="p-2 hover:bg-gray-100 rounded">
            <Settings size={18} />
          </button>
        </div>
      </div>

      {showMemory && (
        <AgentMemoryViewer
          agent={agent}
          onClose={() => setShowMemory(false)}
        />
      )}
    </div>
  );
}
