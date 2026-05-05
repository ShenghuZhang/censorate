'use client';

import { MemberWorkload } from '@/app/hooks/useAnalytics';
import { Users, ArrowUp, ArrowDown } from 'lucide-react';
import { useState } from 'react';

interface WorkloadChartProps {
  data: MemberWorkload[];
}

type SortOrder = 'total' | 'name';

// GitHub-style color palette for swimlanes
const SWIMLANE_COLORS = [
  'bg-[#656d76]',
  'bg-[#0969da]',
  'bg-[#9a6700]',
  'bg-[#1a7f37]',
  'bg-[#8250df]',
  'bg-[#cf222e]',
  'bg-[#0550ae]',
  'bg-[#bc4c00]',
];

const SWIMLANE_TEXT_COLORS = [
  'text-[#656d76]',
  'text-[#0969da]',
  'text-[#9a6700]',
  'text-[#1a7f37]',
  'text-[#8250df]',
  'text-[#cf222e]',
  'text-[#0550ae]',
  'text-[#bc4c00]',
];

export default function WorkloadChart({ data }: WorkloadChartProps) {
  const [sortOrder, setSortOrder] = useState<SortOrder>('total');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Extract all status keys from data (excluding known fields)
  const getStatusKeys = (): string[] => {
    if (data.length === 0) return [];
    const excludedKeys = ['memberId', 'memberName', 'total'];
    return Object.keys(data[0]).filter(key => !excludedKeys.includes(key));
  };

  const statusKeys = getStatusKeys();

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

  // Convert status key to display label
  const formatStatusLabel = (status: string): string => {
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-[#d0d7de] p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-[#1f2328] flex items-center gap-2">
            <Users size={20} className="text-[#0969da]" />
            Member Workload
          </h2>
          <p className="text-sm text-[#656d76] mt-1">
            Requirements per member by status
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => toggleSort('total')}
            className={`flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-full transition-colors ${
              sortOrder === 'total'
                ? 'bg-[#ddf4ff] text-[#0969da]'
                : 'bg-[#f6f8fa] text-[#656d76] hover:bg-[#e6edf3]'
            }`}
          >
            Count
            {sortOrder === 'total' && (
              sortDirection === 'desc' ? <ArrowDown size={14} /> : <ArrowUp size={14} />
            )}
          </button>
          <button
            onClick={() => toggleSort('name')}
            className={`flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-full transition-colors ${
              sortOrder === 'name'
                ? 'bg-[#ddf4ff] text-[#0969da]'
                : 'bg-[#f6f8fa] text-[#656d76] hover:bg-[#e6edf3]'
            }`}
          >
            Name
            {sortOrder === 'name' && (
              sortDirection === 'desc' ? <ArrowDown size={14} /> : <ArrowUp size={14} />
            )}
          </button>
        </div>
      </div>

      {statusKeys.length > 0 && (
        <div className="flex items-center gap-6 mb-6 flex-wrap">
          {statusKeys.map((status, index) => (
            <div key={status} className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded-md ${SWIMLANE_COLORS[index % SWIMLANE_COLORS.length]}`} />
              <span className="text-sm text-[#656d76]">{formatStatusLabel(status)}</span>
            </div>
          ))}
        </div>
      )}

      <div className="space-y-4">
        {sortedData.map((member, index) => {
          // Calculate widths for each status segment
          const statusWidths = statusKeys.map(status => {
            const count = member[status] || 0;
            return {
              status,
              count,
              width: maxTotal > 0 ? (count / maxTotal) * 100 : 0,
            };
          });

          return (
            <div key={member.memberId} className="group">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#656d76] to-[#1f2328] flex items-center justify-center text-white font-medium text-base">
                    {member.memberName.charAt(0).toUpperCase()}
                  </div>
                  <span className="font-medium text-[#1f2328] text-base">
                    {member.memberName}
                  </span>
                </div>
                <div className="text-sm text-[#656d76]">
                  <span className="font-semibold text-[#1f2328] text-base">{member.total}</span> total
                </div>
              </div>

              <div className="flex items-center gap-1 h-10">
                <div className="flex-1 flex h-full rounded-xl overflow-hidden bg-[#f6f8fa]">
                  {statusWidths.map(({ status, count, width }, idx) => (
                    count > 0 && (
                      <div
                        key={status}
                        className={`${SWIMLANE_COLORS[idx % SWIMLANE_COLORS.length]} transition-all h-full flex items-center justify-center`}
                        style={{ width: `${width}%` }}
                      >
                        {width > 10 && (
                          <span className="text-white text-xs font-semibold">
                            {count}
                          </span>
                        )}
                      </div>
                    )
                  ))}
                </div>
              </div>

              <div className="flex justify-between text-xs text-[#656d76] mt-1 flex-wrap gap-2">
                {statusWidths.map(({ status, count }, idx) => (
                  <span key={status}>
                    <span className={`${SWIMLANE_TEXT_COLORS[idx % SWIMLANE_TEXT_COLORS.length]} font-semibold`}>
                      {count}
                    </span> {formatStatusLabel(status)}
                  </span>
                ))}
              </div>
            </div>
          );
        })}

        {sortedData.length === 0 && (
          <div className="text-center py-12">
            <p className="text-[#656d76]">No members found</p>
          </div>
        )}
      </div>
    </div>
  );
}
