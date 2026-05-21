'use client';

import type { PipelineStep } from '@/lib/api/generation-projects';
import { clsx } from 'clsx';

const STEP_LABELS: Record<string, string> = {
  analysis: 'Requirement Analysis',
  architecture: 'Architecture Design',
  code_generation: 'Code Generation',
  code_review: 'Code Review',
  github_push: 'GitHub Push',
};

const STEP_ORDER = ['analysis', 'architecture', 'code_generation', 'code_review', 'github_push'];

interface PipelineProgressProps {
  steps: PipelineStep[];
}

export default function PipelineProgress({ steps }: PipelineProgressProps) {
  if (steps.length === 0) {
    return (
      <div className="text-sm text-gray-500 text-center py-4">
        Pipeline not started yet
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {STEP_ORDER.map((stepType) => {
        const step = steps.find((s) => s.step_type === stepType);
        const label = STEP_LABELS[stepType] || stepType;
        let statusIcon = '○';
        let statusClass = 'text-gray-400';

        if (step) {
          if (step.status === 'running') {
            statusIcon = '◌';
            statusClass = 'text-blue-500 animate-pulse';
          } else if (step.status === 'completed') {
            statusIcon = '●';
            statusClass = 'text-green-500';
          } else if (step.status === 'failed') {
            statusIcon = '●';
            statusClass = 'text-red-500';
          }
        }

        return (
          <div key={stepType} className="flex items-center gap-3">
            <span className={clsx('text-lg font-bold', statusClass)}>{statusIcon}</span>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className={clsx(
                  'text-sm font-medium',
                  step?.status === 'failed' && 'text-red-700',
                  step?.status === 'completed' && 'text-green-700',
                  (!step || step.status === 'pending') && 'text-gray-400',
                )}>
                  {label}
                </span>
                {step?.status === 'running' && (
                  <span className="text-xs text-blue-600 font-medium">In progress...</span>
                )}
                {step?.status === 'completed' && step.completed_at && (
                  <span className="text-xs text-green-600">
                    {new Date(step.completed_at).toLocaleTimeString()}
                  </span>
                )}
                {step?.status === 'failed' && (
                  <span className="text-xs text-red-600 font-medium">Failed</span>
                )}
                {step?.retry_count && step.retry_count > 0 && (
                  <span className="text-xs text-amber-600 ml-2">(retry {step.retry_count})</span>
                )}
              </div>
              {step?.error && (
                <p className="text-xs text-red-600 mt-0.5 truncate">{step.error}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
