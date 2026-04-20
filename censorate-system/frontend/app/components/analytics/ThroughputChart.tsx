'use client';

import { useState } from 'react';
import { DailyThroughput } from '@/app/hooks/useAnalytics';
import { TrendingUp, AlertTriangle } from 'lucide-react';

interface ThroughputChartProps {
  data: DailyThroughput[];
}

type TimeRange = '7d' | '14d' | '30d';

export default function ThroughputChart({ data }: ThroughputChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('14d');

  const filteredData = data.slice(timeRange === '7d' ? -7 : timeRange === '14d' ? -14 : -30);
  const maxCount = Math.max(...filteredData.map(d => Math.max(d.created, d.completed)), 1);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-soft border border-border p-6 mb-8 animate-fade-in-up" style={{ animationDelay: '150ms' }}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
            <TrendingUp size={20} className="text-primary" />
            Daily Throughput
          </h2>
          <p className="text-sm text-text-muted mt-1">
            Track requirement creation and completion over time
          </p>
        </div>

        <div className="flex items-center gap-2">
          {(['7d', '14d', '30d'] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                timeRange === range
                  ? 'bg-primary text-white'
                  : 'bg-surface-soft text-text-secondary hover:bg-surface-softer'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-6 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span className="text-sm text-text-secondary">Created</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-sm text-text-secondary">Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <AlertTriangle size={16} className="text-warning" />
          <span className="text-sm text-text-secondary">Overloaded</span>
        </div>
      </div>

      <div className="h-64 flex items-end gap-2 px-2">
        {filteredData.map((day, index) => {
          const createdHeight = (day.created / maxCount) * 100;
          const completedHeight = (day.completed / maxCount) * 100;

          return (
            <div
              key={day.date}
              className="flex-1 flex flex-col items-center gap-1 group"
            >
              <div className="w-full flex items-end gap-1 h-48">
                <div className="flex-1 flex flex-col justify-end">
                  <div
                    className={`w-full bg-blue-500 rounded-t-md transition-all group-hover:bg-blue-600 ${
                      day.isOverload ? 'ring-2 ring-warning' : ''
                    }`}
                    style={{ height: `${createdHeight}%` }}
                  />
                </div>
                <div className="flex-1 flex flex-col justify-end">
                  <div
                    className="w-full bg-green-500 rounded-t-md transition-all group-hover:bg-green-600"
                    style={{ height: `${completedHeight}%` }}
                  />
                </div>
              </div>

              <div className="text-xs text-text-muted text-center">
                {formatDate(day.date)}
              </div>

              <div className="absolute bottom-20 bg-surface border border-border rounded-lg p-2 shadow-elevated opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 text-xs whitespace-nowrap">
                <div className="text-text-secondary">
                  <span className="text-blue-600 font-semibold">{day.created}</span> created
                </div>
                <div className="text-text-secondary">
                  <span className="text-green-600 font-semibold">{day.completed}</span> completed
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
