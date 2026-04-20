'use client';

import { TeamMember, AIAgent } from '@/app/stores/teamStore';
import { User, Brain, MoreHorizontal, Trash2, Settings } from 'lucide-react';
import { useState } from 'react';
import { clsx } from 'clsx';

type Member = TeamMember | AIAgent;

interface MemberCardProps {
  member: Member;
  onRemove?: (id: string) => void;
}

export default function MemberCard({ member, onRemove }: MemberCardProps) {
  const [showMenu, setShowMenu] = useState(false);
  const isAI = (m: Member): m is AIAgent => m.type === 'ai';

  return (
    <div className="bg-white rounded-lg shadow-soft border border-border p-5 hover:shadow-medium transition-all group">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          {/* Avatar */}
          <div className={clsx(
            'w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-soft',
            isAI(member)
              ? 'bg-gradient-to-br from-purple-500 to-blue-500'
              : 'bg-gradient-to-br from-gray-400 to-gray-600'
          )}>
            {isAI(member) ? (
              <Brain size={24} />
            ) : (
              (member.name || member.nickname).charAt(0).toUpperCase()
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-text-primary text-base">
              {member.nickname || member.name}
            </h3>
            {member.name !== member.nickname && (
              <p className="text-sm text-text-muted">{member.name}</p>
            )}

            {/* Type badge */}
            <div className="flex items-center gap-2 mt-3">
              <span className={clsx(
                'text-xs font-bold px-2.5 py-1 rounded-lg uppercase tracking-wide',
                isAI(member)
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-gray-100 text-gray-600'
              )}>
                {isAI(member) ? 'AI Agent' : 'Human'}
              </span>
              <span className="text-sm text-text-muted">
                {member.role.replace('_', ' ')}
              </span>
            </div>

            {/* AI Skills */}
            {isAI(member) && member.skills && member.skills.length > 0 && (
              <div className="mt-3">
                <div className="flex flex-wrap gap-1.5">
                  {member.skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="text-xs bg-surface-soft text-text-secondary px-2 py-1 rounded-md"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* AI Memory Status */}
            {isAI(member) && (
              <div className="flex items-center gap-2 mt-3">
                <div className={clsx(
                  'w-2.5 h-2.5 rounded-full',
                  member.memoryEnabled ? 'bg-success' : 'bg-gray-300'
                )} />
                <span className="text-xs text-text-muted">
                  Memory: {member.memoryEnabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Menu */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 hover:bg-surface-soft rounded-lg transition-colors opacity-0 group-hover:opacity-100"
          >
            <MoreHorizontal size={18} className="text-text-muted" />
          </button>

          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowMenu(false)}
              />
              <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg border border-border shadow-medium z-20 py-1">
                {isAI(member) && (
                  <button className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-text-secondary hover:bg-surface-soft transition-colors">
                    <Settings size={16} />
                    Configure Agent
                  </button>
                )}
                {onRemove && (
                  <button
                    onClick={() => {
                      onRemove(member.id);
                      setShowMenu(false);
                    }}
                    className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-error hover:bg-error-soft transition-colors"
                  >
                    <Trash2 size={16} />
                    Remove
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border-light flex items-center justify-between">
        <span className="text-xs text-text-muted">
          Joined {new Date(member.joinedAt).toLocaleDateString()}
        </span>
        {member.status === 'active' ? (
          <span className="flex items-center gap-1.5 text-xs text-success">
            <span className="w-1.5 h-1.5 bg-success rounded-full" />
            Active
          </span>
        ) : (
          <span className="text-xs text-text-muted">Inactive</span>
        )}
      </div>
    </div>
  );
}
