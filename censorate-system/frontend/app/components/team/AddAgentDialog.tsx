'use client';

import { useState } from 'react';
import { useTeamStore } from '@/app/stores/teamStore';
import { X } from 'lucide-react';

interface AddAgentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  existingRoles: string[];
}

export default function AddAgentDialog({ isOpen, onClose, existingRoles }: AddAgentDialogProps) {
  const [name, setName] = useState('');
  const [nickname, setNickname] = useState('');
  const [role, setRole] = useState('');
  const [skills, setSkills] = useState<string[]>([]);
  const [memoryEnabled, setMemoryEnabled] = useState(true);
  const [skillInput, setSkillInput] = useState('');
  const { addAgent } = useTeamStore();
  const projectId = '58d22de7-ddfd-4996-be3d-48e29599604d'; // 在实际应用中，项目 ID 应该来自 URL 参数或全局状态

  const availableRoles = [
    'analysis_agent',
    'design_agent',
    'development_agent',
    'testing_agent',
    'review_agent'
  ].filter(r => !existingRoles.includes(r));

  const handleAddSkill = () => {
    if (skillInput.trim() && !skills.includes(skillInput.trim())) {
      setSkills([...skills, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setSkills(skills.filter(skill => skill !== skillToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addAgent(projectId, {
        name,
        nickname,
        role,
        skills,
        memoryEnabled,
        agentType: role.replace('_agent', ''),
        deepagentConfig: {},
        status: 'active'
      });
      onClose();
    } catch (error) {
      console.error('Failed to add agent:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl w-full max-w-md max-h-[80vh] overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-bold">Add AI Agent</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Agent Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="e.g., Analysis Agent"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nickname
              </label>
              <input
                type="text"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                placeholder="e.g., Alex"
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

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Skills
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  placeholder="Enter skill"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                />
                <button
                  type="button"
                  onClick={handleAddSkill}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {skills.map((skill, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 text-sm bg-gray-100 rounded flex items-center gap-1"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => handleRemoveSkill(skill)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
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

            <div className="flex justify-end gap-3 pt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!role || !name}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                Add AI Agent
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
