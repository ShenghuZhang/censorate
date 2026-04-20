'use client';

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { AIAgent } from '@/app/stores/teamStore';

interface AgentMemoryViewerProps {
  agent: AIAgent;
  onClose: () => void;
}

export default function AgentMemoryViewer({ agent, onClose }: AgentMemoryViewerProps) {
  const [memory, setMemory] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadMemory();
  }, [agent.id]);

  const loadMemory = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/agents/${agent.id}/memory`);
      const data = await response.json();
      setMemory(data);
    } catch (error) {
      console.error('Failed to load agent memory:', error);
    }
    setIsLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl w-full max-w-4xl max-h-[80vh] overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-xl font-bold">{agent.nickname} Memory</h2>
            <p className="text-sm text-gray-500">
              Long-term memory stored locally as document
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin w-8 h-8 border-2 border-blue-600 rounded-full border-t-transparent" />
            </div>
          ) : memory ? (
            <div className="bg-gray-50 rounded-lg p-6">
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(memory, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>No memory data available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
