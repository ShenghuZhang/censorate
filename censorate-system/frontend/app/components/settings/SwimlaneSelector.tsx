'use client';

import { useState, useEffect } from 'react';
import { clsx } from 'clsx';

const PRESET_OPTIONS = [
  {
    id: 'default',
    label: 'Default (4 lanes)',
    lanes: ['Backlog', 'Todo', 'In Review', 'Done'],
  },
  {
    id: 'standard',
    label: 'Standard (6 lanes)',
    lanes: ['需求', '需求分析', '方案设计', '开发', '测试', '完成'],
  },
  {
    id: 'custom',
    label: 'Custom',
    lanes: [],
  },
];

export const DEFAULT_LANES = PRESET_OPTIONS[0].lanes;

interface SwimlaneSelectorProps {
  value?: string[];
  onChange: (lanes: string[]) => void;
  error?: string;
}

// Convert display name to valid ID (snake_case)
export function slugifyLaneName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '_')
    .replace(/^_|_$/g, '')
    || `lane_${Date.now()}`;
}

// Get lane colors based on index
export function getLaneColors(index: number, total: number) {
  if (index === 0) {
    return { color: 'bg-gray-50/50', badgeColor: 'bg-gray-600 text-white' };
  }
  if (index === total - 1) {
    return { color: 'bg-green-50/50', badgeColor: 'bg-green-600 text-white' };
  }
  const middleColors = [
    { color: 'bg-blue-50/50', badgeColor: 'bg-blue-600 text-white' },
    { color: 'bg-amber-50/50', badgeColor: 'bg-amber-600 text-white' },
    { color: 'bg-purple-50/50', badgeColor: 'bg-purple-600 text-white' },
    { color: 'bg-pink-50/50', badgeColor: 'bg-pink-600 text-white' },
  ];
  return middleColors[(index - 1) % middleColors.length];
}

export default function SwimlaneSelector({ value, onChange, error }: SwimlaneSelectorProps) {
  const [selectedPreset, setSelectedPreset] = useState<string>('default');
  const [customInput, setCustomInput] = useState('');

  // Initialize from value
  useEffect(() => {
    if (value && value.length > 0) {
      const matchingPreset = PRESET_OPTIONS.find(
        opt => opt.id !== 'custom' &&
        JSON.stringify(opt.lanes) === JSON.stringify(value)
      );
      if (matchingPreset) {
        setSelectedPreset(matchingPreset.id);
        setCustomInput('');
      } else {
        setSelectedPreset('custom');
        setCustomInput(value.join(', '));
      }
    } else {
      setSelectedPreset('default');
      setCustomInput('');
    }
  }, [value]);

  const handlePresetChange = (presetId: string) => {
    setSelectedPreset(presetId);
    const preset = PRESET_OPTIONS.find(opt => opt.id === presetId);
    if (preset && preset.id !== 'custom') {
      setCustomInput('');
      onChange(preset.lanes);
    }
  };

  const handleCustomInputChange = (input: string) => {
    setCustomInput(input);
    const lanes = input
      .split(',')
      .map(l => l.trim())
      .filter(l => l.length > 0);
    onChange(lanes);
  };

  const displayLanes = selectedPreset === 'custom'
    ? customInput.split(',').map(l => l.trim()).filter(l => l.length > 0)
    : PRESET_OPTIONS.find(opt => opt.id === selectedPreset)?.lanes || [];

  const isValid = displayLanes.length >= 2 && displayLanes.length <= 10;

  return (
    <div className="space-y-7">
      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-5">
          Swimlane Configuration
        </label>

        {/* Preset options */}
        <div className="grid grid-cols-1 gap-4 mb-7">
          {PRESET_OPTIONS.map((preset) => (
            <button
              key={preset.id}
              type="button"
              onClick={() => handlePresetChange(preset.id)}
              className={clsx(
                'flex items-center justify-between p-5 rounded-2xl border-2 transition-all duration-200 text-left',
                selectedPreset === preset.id
                  ? 'border-slate-400 bg-slate-100 shadow-md'
                  : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-slate-100/70'
              )}
            >
              <span className={clsx(
                'font-semibold text-base',
                selectedPreset === preset.id ? 'text-slate-800' : 'text-slate-600'
              )}>
                {preset.label}
              </span>
              {preset.id !== 'custom' && (
                <span className="text-sm text-slate-500 font-medium bg-white/60 px-3 py-1 rounded-full border border-slate-200">
                  {preset.lanes.length} lanes
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Custom input */}
        {selectedPreset === 'custom' && (
          <div className="space-y-3 mb-7">
            <label className="block text-sm font-medium text-slate-600">
              Enter lane names (comma-separated)
            </label>
            <input
              type="text"
              value={customInput}
              onChange={(e) => handleCustomInputChange(e.target.value)}
              placeholder="Backlog, Todo, In Review, Done"
              className={clsx(
                'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-300 focus:border-slate-400 outline-none transition-all duration-200 text-slate-700 text-sm shadow-sm',
                error ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-200' : ''
              )}
            />
          </div>
        )}
      </div>

      {/* Validation message */}
      {displayLanes.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Preview
            </span>
            <span className={clsx(
              'text-sm font-semibold',
              isValid ? 'text-emerald-600' : 'text-rose-600'
            )}>
              {displayLanes.length} {displayLanes.length === 1 ? 'lane' : 'lanes'}
              {!isValid && ` (needs 2-10)`}
            </span>
          </div>

          {/* Lane preview - Kanban style */}
          <div className="flex gap-2 overflow-x-auto pb-2">
            {displayLanes.map((lane, index) => {
              const colors = getLaneColors(index, displayLanes.length);
              return (
                <div
                  key={`${slugifyLaneName(lane)}-${index}`}
                  className={clsx(
                    'flex-shrink-0 min-w-[120px] max-w-[160px] px-3.5 py-2.5 rounded-xl text-sm font-medium border border-slate-200 shadow-sm text-center',
                    colors.color
                  )}
                >
                  <span className="text-slate-700 truncate block">{lane}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {error && (
        <p className="text-sm text-rose-600 font-medium bg-rose-50 px-4 py-2 rounded-xl border border-rose-100 w-fit">
          {error}
        </p>
      )}
    </div>
  );
}
