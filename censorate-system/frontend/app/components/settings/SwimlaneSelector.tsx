'use client';

import { useState, useEffect } from 'react';
import { clsx } from 'clsx';
import { Check } from 'lucide-react';

const PRESET_OPTIONS = [
  {
    id: 'default',
    label: 'Default',
    description: 'Simple workflow for small teams',
    lanes: ['Backlog', 'Todo', 'In Review', 'Done'],
  },
  {
    id: 'standard',
    label: 'Standard',
    description: 'Full workflow for product development',
    lanes: ['需求', '需求分析', '方案设计', '开发', '测试', '完成'],
  },
  {
    id: 'custom',
    label: 'Custom',
    description: 'Define your own workflow',
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

// Get lane colors based on index - GitHub style muted colors
export function getLaneColors(index: number, total: number) {
  const colors = [
    { bg: 'bg-gray-100', border: 'border-gray-300', text: 'text-gray-700' },
    { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700' },
    { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700' },
    { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700' },
    { bg: 'bg-pink-50', border: 'border-pink-200', text: 'text-pink-700' },
    { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700' },
    { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700' },
    { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700' },
    { bg: 'bg-teal-50', border: 'border-teal-200', text: 'text-teal-700' },
    { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-700' },
  ];
  return colors[index % colors.length];
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
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-4">
          Workflow
        </h3>

        {/* Preset options - GitHub style radio cards */}
        <div className="space-y-2 mb-6">
          {PRESET_OPTIONS.map((preset) => (
            <label
              key={preset.id}
              className={clsx(
                'flex items-start gap-4 p-4 rounded-lg border transition-all cursor-pointer',
                selectedPreset === preset.id
                  ? 'border-blue-500 bg-blue-50/50'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
              )}
            >
              <div className="flex items-center justify-center mt-0.5">
                <div className={clsx(
                  'w-4 h-4 rounded-full border flex items-center justify-center transition-all',
                  selectedPreset === preset.id
                    ? 'border-blue-600'
                    : 'border-gray-300'
                )}>
                  {selectedPreset === preset.id && (
                    <div className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                  )}
                </div>
              </div>

              <div className="flex-1" onClick={() => handlePresetChange(preset.id)}>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">
                    {preset.label}
                  </span>
                  {preset.id !== 'custom' && (
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                      {preset.lanes.length} lanes
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  {preset.description}
                </p>
              </div>
            </label>
          ))}
        </div>

        {/* Custom input - GitHub style input */}
        {selectedPreset === 'custom' && (
          <div className="space-y-3 mb-6 border-t border-gray-200 pt-6">
            <label className="block text-sm font-medium text-gray-700">
              Lane names
            </label>
            <div className="text-sm text-gray-500 mb-2">
              Separate lane names with commas
            </div>
            <input
              type="text"
              value={customInput}
              onChange={(e) => handleCustomInputChange(e.target.value)}
              placeholder="Backlog, Todo, In Progress, Review, Done"
              className={clsx(
                'w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition-all text-sm text-gray-900 placeholder:text-gray-400',
                error ? 'border-red-300 focus:border-red-500 focus:ring-red-500/30' : ''
              )}
            />
          </div>
        )}
      </div>

      {/* Preview section */}
      {displayLanes.length > 0 && (
        <div className="border-t border-gray-200 pt-6">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Preview
            </h4>
            <span className={clsx(
              'text-sm',
              isValid ? 'text-green-600' : 'text-red-600'
            )}>
              <span className="font-medium">{displayLanes.length}</span> {displayLanes.length === 1 ? 'lane' : 'lanes'}
              {!isValid && <span className="text-gray-500 ml-1">(2-10 required)</span>}
            </span>
          </div>

          {/* Lane preview - GitHub style labels */}
          <div className="flex flex-wrap gap-2">
            {displayLanes.map((lane, index) => {
              const colors = getLaneColors(index, displayLanes.length);
              return (
                <span
                  key={`${slugifyLaneName(lane)}-${index}`}
                  className={clsx(
                    'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border',
                    colors.bg,
                    colors.border,
                    colors.text
                  )}
                >
                  {lane}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {error && (
        <div className="pt-4 border-t border-gray-200">
          <p className="text-sm text-red-600 flex items-center gap-2">
            <Check className="w-4 h-4" />
            {error}
          </p>
        </div>
      )}
    </div>
  );
}
