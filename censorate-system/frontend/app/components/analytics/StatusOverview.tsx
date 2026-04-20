'use client';

import { StatusStats } from '@/app/hooks/useAnalytics';
import { Circle, Clock, CheckCircle2, FolderKanban } from 'lucide-react';

interface StatusOverviewProps {
  stats: StatusStats[];
  total: number;
}

const getStatusIcon = (status: string) => {
  switch (status.toLowerCase()) {
    case 'todo':
      return <Clock size={24} className="text-white" />;
    case 'in review':
      return <CheckCircle2 size={24} className="text-white" />;
    case 'done':
      return <CheckCircle2 size={24} className="text-white" />;
    default:
      return <Circle size={24} className="text-white" />;
  }
};

export default function StatusOverview({ stats, total }: StatusOverviewProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      {stats.map((stat, index) => {
        const percentage = total > 0 ? Math.round((stat.count / total) * 100) : 0;

        return (
          <div
            key={stat.status}
            className="bg-white rounded-lg shadow-soft border border-border p-6 hover:shadow-medium transition-all animate-fade-in-up"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`p-3 rounded-lg ${stat.color} shadow-soft`}>
                {getStatusIcon(stat.label)}
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-text-primary">
                  {stat.count}
                </span>
                {total > 0 && (
                  <div className="text-xs text-text-muted mt-1">
                    {percentage}%
                  </div>
                )}
              </div>
            </div>

            <h3 className="font-semibold text-text-secondary mb-2">
              {stat.label}
            </h3>

            <div className="w-full h-2 bg-surface-softer rounded-full overflow-hidden">
              <div
                className={`h-full ${stat.color} transition-all duration-500`}
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
