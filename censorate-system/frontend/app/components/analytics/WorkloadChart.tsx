'use client';

import { MemberWorkload } from '@/app/hooks/useAnalytics';
import { Users, ArrowUp, ArrowDown } from 'lucide-react';
import { useState } from 'react';

interface WorkloadChartProps {
  data: MemberWorkload[];
}

type SortOrder = 'total' | 'name';

export default function WorkloadChart({ data }: WorkloadChartProps) {
  const [sortOrder, setSortOrder] = useState<SortOrder>('total');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const sortedData = [...data].sort((a, b) => {
    if (sortOrder === 'total') {
      return sortDirection === 'desc' ? b.total - a.total : a.total - b.total;
    } else {
      return sortDirection === 'desc'
        ? b.memberName.localeCompare(a.memberName)
        : a.memberName.localeCompare(b.memberName);
    }
  });

  const maxTotal = Math.max(...data.map(d => d.total), 1);

  const toggleSort = (order: SortOrder) => {
    if (sortOrder === order) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortOrder(order);
      setSortDirection('desc');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-soft border border-border p-6 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
            <Users size={20} className="text-primary" />
            Member Workload
          </h2>
          <p className="text-sm text-text-muted mt-1">
            Requirements per member by status
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => toggleSort('total')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
              sortOrder === 'total'
                ? 'bg-primary-soft text-primary'
                : 'bg-surface-soft text-text-secondary hover:bg-surface-softer'
            }`}
          >
            Count
            {sortOrder === 'total' && (
              sortDirection === 'desc' ? <ArrowDown size={14} /> : <ArrowUp size={14} />
            )}
          </button>
          <button
            onClick={() => toggleSort('name')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
              sortOrder === 'name'
                ? 'bg-primary-soft text-primary'
                : 'bg-surface-soft text-text-secondary hover:bg-surface-softer'
            }`}
          >
            Name
            {sortOrder === 'name' && (
              sortDirection === 'desc' ? <ArrowDown size={14} /> : <ArrowUp size={14} />
            )}
          </button>
        </div>
      </div>

      <div className="flex items-center gap-6 mb-6">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-md bg-blue-500" />
          <span className="text-sm text-text-secondary">Todo</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-md bg-amber-500" />
          <span className="text-sm text-text-secondary">In Review</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-md bg-green-500" />
          <span className="text-sm text-text-secondary">Done</span>
        </div>
      </div>

      <div className="space-y-4">
        {sortedData.map((member, index) => {
          const todoWidth = maxTotal > 0 ? (member.todo / maxTotal) * 100 : 0;
          const inReviewWidth = maxTotal > 0 ? (member.inReview / maxTotal) * 100 : 0;
          const doneWidth = maxTotal > 0 ? (member.done / maxTotal) * 100 : 0;

          return (
            <div key={member.memberId} className="group">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-medium text-sm">
                    {member.memberName.charAt(0).toUpperCase()}
                  </div>
                  <span className="font-medium text-text-primary">
                    {member.memberName}
                  </span>
                </div>
                <div className="text-sm text-text-muted">
                  <span className="font-semibold text-text-primary">{member.total}</span> total
                </div>
              </div>

              <div className="flex items-center gap-1 h-8">
                <div className="flex-1 flex h-full rounded-lg overflow-hidden bg-surface-soft">
                  {member.todo > 0 && (
                    <div
                      className="bg-blue-500 transition-all h-full flex items-center justify-center"
                      style={{ width: `${todoWidth}%` }}
                    >
                      {todoWidth > 10 && (
                        <span className="text-white text-xs font-semibold">
                          {member.todo}
                        </span>
                      )}
                    </div>
                  )}
                  {member.inReview > 0 && (
                    <div
                      className="bg-amber-500 transition-all h-full flex items-center justify-center"
                      style={{ width: `${inReviewWidth}%` }}
                    >
                      {inReviewWidth > 10 && (
                        <span className="text-white text-xs font-semibold">
                          {member.inReview}
                        </span>
                      )}
                    </div>
                  )}
                  {member.done > 0 && (
                    <div
                      className="bg-green-500 transition-all h-full flex items-center justify-center"
                      style={{ width: `${doneWidth}%` }}
                    >
                      {doneWidth > 10 && (
                        <span className="text-white text-xs font-semibold">
                          {member.done}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-between text-xs text-text-muted mt-1">
                <span>
                  <span className="text-blue-600 font-semibold">{member.todo}</span> todo
                </span>
                <span>
                  <span className="text-amber-600 font-semibold">{member.inReview}</span> in review
                </span>
                <span>
                  <span className="text-green-600 font-semibold">{member.done}</span> done
                </span>
              </div>
            </div>
          );
        })}

        {sortedData.length === 0 && (
          <div className="text-center py-12">
            <p className="text-text-muted">No members found</p>
          </div>
        )}
      </div>
    </div>
  );
}
