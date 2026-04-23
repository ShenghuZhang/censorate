'use client';

import { StatusStats } from '@/app/hooks/useAnalytics';
import { Circle, Clock, CheckCircle2, FolderKanban } from 'lucide-react';

interface StatusOverviewProps {
  stats: StatusStats[];
  total: number;
}

const getStatusIcon = (index: number, label: string) => {
  // Use different icons based on index or label
  const lowerLabel = label.toLowerCase();
  if (lowerLabel.includes('done') || lowerLabel.includes('complete') || lowerLabel.includes('finish')) {
    return <CheckCircle2 size={24} className="text-white" />;
  }
  if (lowerLabel.includes('review') || lowerLabel.includes('verify')) {
    return <CheckCircle2 size={24} className="text-white" />;
  }
  if (lowerLabel.includes('todo') || lowerLabel.includes('to do') || lowerLabel.includes('next')) {
    return <Clock size={24} className="text-white" />;
  }
  if (lowerLabel.includes('backlog') || lowerLabel.includes('back log')) {
    return <FolderKanban size={24} className="text-white" />;
  }
  // Fallback based on index
  const icons = [<Circle size={24} className="text-white" />, <Clock size={24} className="text-white" />, <CheckCircle2 size={24} className="text-white" />, <FolderKanban size={24} className="text-white" />];
  return icons[index % icons.length];
};

export default function StatusOverview({ stats, total }: StatusOverviewProps) {
  // Determine grid columns based on number of stats
  const getGridCols = () => {
    if (stats.length <= 2) return 'grid-cols-1 sm:grid-cols-2';
    if (stats.length <= 4) return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4';
    return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4';
  };

  return (
    <div className={`grid ${getGridCols()} gap-5 mb-8`}>
      {stats.map((stat, index) => {
        const percentage = total > 0 ? Math.round((stat.count / total) * 100) : 0;

        return (
          <div
            key={stat.status}
            className="bg-white rounded-2xl shadow-soft border border-border p-6 hover:shadow-medium transition-all animate-fade-in-up"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`p-4 rounded-2xl ${stat.color} shadow-soft`}>
                {getStatusIcon(index, stat.label)}
              </div>
              <div className="text-right">
                <span className="text-4xl font-bold text-text-primary">
                  {stat.count}
                </span>
                {total > 0 && (
                  <div className="text-sm text-text-muted mt-1">
                    {percentage}%
                  </div>
                )}
              </div>
            </div>

            <h3 className="text-xl font-semibold text-text-secondary mb-3">
              {stat.label}
            </h3>

            <div className="w-full h-3 bg-surface-softer rounded-full overflow-hidden">
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
