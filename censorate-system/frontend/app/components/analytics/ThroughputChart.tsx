'use client';

import { useState } from 'react';
import { DailyThroughput } from '@/app/hooks/useAnalytics';
import { TrendingUp } from 'lucide-react';

interface ThroughputChartProps {
  data: DailyThroughput[];
}

type TimeRange = '7d' | '14d' | '30d';

export default function ThroughputChart({ data }: ThroughputChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('14d');

  const filteredData = data.slice(timeRange === '7d' ? -7 : timeRange === '14d' ? -14 : -30);
  const maxCount = Math.max(...filteredData.map(d => Math.max(d.completed, d.backlog)), 1);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const hasData = filteredData.some(d => d.completed > 0 || d.backlog > 0);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-[#d0d7de] p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-[#1f2328] flex items-center gap-2">
            <TrendingUp size={20} className="text-[#0969da]" />
            Daily Throughput
          </h2>
          <p className="text-sm text-[#656d76] mt-1">
            Track completed work and backlog over time
          </p>
        </div>

        <div className="flex items-center gap-2">
          {(['7d', '14d', '30d'] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-colors ${
                timeRange === range
                  ? 'bg-[#0969da] text-white'
                  : 'bg-[#f6f8fa] text-[#656d76] hover:bg-[#e6edf3]'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {!hasData ? (
        <div className="h-64 flex items-center justify-center text-[#656d76]">
          <p>No data yet. Create some requirements to see the chart!</p>
        </div>
      ) : (
        <>
          <div className="flex items-center gap-6 mb-4 flex-wrap">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-[#1a7f37]" />
              <span className="text-sm text-[#656d76]">Completed Today</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-[#0969da]" />
              <span className="text-sm text-[#656d76]">Backlog</span>
            </div>
          </div>

          <div className="h-64 flex items-end gap-2 px-2">
            {filteredData.map((day, index) => {
              const completedHeight = (day.completed / maxCount) * 100;
              const backlogHeight = (day.backlog / maxCount) * 100;

              return (
                <div
                  key={day.date}
                  className="flex-1 flex flex-col items-center gap-1 group relative"
                >
                  <div className="w-full flex items-end gap-1 h-48">
                    {/* Completed column */}
                    <div className="flex-1 flex flex-col justify-end">
                      {day.completed > 0 ? (
                        <div
                          className="w-full bg-[#1a7f37] rounded-t-md transition-all group-hover:bg-[#1f883d]"
                          style={{ height: `${completedHeight}%` }}
                        />
                      ) : (
                        <div className="w-full h-1 bg-[#f6f8fa] rounded" />
                      )}
                    </div>
                    {/* Backlog column */}
                    <div className="flex-1 flex flex-col justify-end">
                      {day.backlog > 0 ? (
                        <div
                          className="w-full bg-[#0969da] rounded-t-md transition-all group-hover:bg-[#218bff]"
                          style={{ height: `${backlogHeight}%` }}
                        />
                      ) : (
                        <div className="w-full h-1 bg-[#f6f8fa] rounded" />
                      )}
                    </div>
                  </div>

                  <div className="text-xs text-[#656d76] text-center">
                    {formatDate(day.date)}
                  </div>

                  <div className="absolute bottom-20 bg-white border border-[#d0d7de] rounded-lg p-3 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 text-xs whitespace-nowrap">
                    <div className="text-[#656d76] mb-1">
                      <span className="text-[#1a7f37] font-semibold">{day.completed}</span> completed
                    </div>
                    <div className="text-[#656d76]">
                      <span className="text-[#0969da] font-semibold">{day.backlog}</span> backlog
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
