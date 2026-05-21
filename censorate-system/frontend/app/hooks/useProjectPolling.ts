'use client';
import { useEffect, useRef } from 'react';
import { useGenerationProjectStore } from '@/app/stores/generationProjectStore';

const ACTIVE_STATUSES = ['draft', 'confirmed', 'designing', 'generating', 'reviewing', 'ready', 'pushing'];
const POLL_INTERVAL = 3000;

export function useProjectPolling(projectId: string | null) {
  const fetchProject = useGenerationProjectStore((s) => s.fetchProject);
  const currentProject = useGenerationProjectStore((s) => s.currentProject);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const isActive = currentProject
      ? ACTIVE_STATUSES.includes(currentProject.status)
      : true;

    if (isActive) {
      intervalRef.current = setInterval(() => {
        fetchProject(projectId);
      }, POLL_INTERVAL);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [projectId, currentProject?.status, fetchProject]);
}
