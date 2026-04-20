'use client';

import { useState, useEffect, useCallback } from 'react';
import { RequirementStatus } from '@/app/stores/requirementStore';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8216/api/v1';

function snakeToCamel(obj: any): any {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => snakeToCamel(item));
  }

  return Object.keys(obj).reduce((result, key) => {
    const camelKey = key.replace(/(_\w)/g, match => match[1].toUpperCase());
    result[camelKey] = snakeToCamel(obj[key]);
    return result;
  }, {} as any);
}

export interface StatusStats {
  status: RequirementStatus;
  count: number;
  label: string;
  color: string;
  bgColor: string;
  percentage: number;
}

export interface DailyThroughput {
  date: string;
  created: number;
  completed: number;
  isOverload: boolean;
}

export interface MemberWorkload {
  memberId: string;
  memberName: string;
  todo: number;
  inReview: number;
  done: number;
  total: number;
}

const STATUS_CONFIG: Record<RequirementStatus, { label: string; color: string; bgColor: string }> = {
  backlog: { label: 'Backlog', color: 'bg-gray-500', bgColor: 'bg-gray-100' },
  todo: { label: 'Todo', color: 'bg-blue-500', bgColor: 'bg-blue-100' },
  in_review: { label: 'In Review', color: 'bg-amber-500', bgColor: 'bg-amber-100' },
  done: { label: 'Done', color: 'bg-green-500', bgColor: 'bg-green-100' },
};

interface AnalyticsData {
  statusStats: StatusStats[];
  dailyThroughput: DailyThroughput[];
  memberWorkload: MemberWorkload[];
  totalRequirements: number;
}

export function useAnalytics(projectId: string | null) {
  const [data, setData] = useState<AnalyticsData>({
    statusStats: [],
    dailyThroughput: [],
    memberWorkload: [],
    totalRequirements: 0,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async () => {
    if (!projectId) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const [statsRes, throughputRes, workloadRes] = await Promise.all([
        fetch(`${API_BASE_URL}/projects/${projectId}/analytics`),
        fetch(`${API_BASE_URL}/projects/${projectId}/analytics/throughput?days=14`),
        fetch(`${API_BASE_URL}/projects/${projectId}/analytics/workload`),
      ]);

      if (!statsRes.ok || !throughputRes.ok || !workloadRes.ok) {
        throw new Error('Failed to fetch analytics data');
      }

      const statsData = snakeToCamel(await statsRes.json());
      const throughputData = snakeToCamel(await throughputRes.json());
      const workloadData = snakeToCamel(await workloadRes.json());

      const statusStats: StatusStats[] = (statsData.statusDistribution || []).map((item: any) => ({
        status: item.status as RequirementStatus,
        count: item.count,
        percentage: item.percentage,
        ...STATUS_CONFIG[item.status as RequirementStatus],
      }));

      const dailyThroughput: DailyThroughput[] = throughputData.map((item: any) => ({
        date: item.date,
        created: item.created,
        completed: item.completed,
        isOverload: item.isOverload,
      }));

      const memberWorkload: MemberWorkload[] = workloadData.map((item: any) => ({
        memberId: item.memberId,
        memberName: item.memberName,
        todo: item.todo,
        inReview: item.inReview,
        done: item.done,
        total: item.total,
      }));

      setData({
        statusStats,
        dailyThroughput,
        memberWorkload,
        totalRequirements: statsData.totalRequirements || 0,
      });
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  return {
    ...data,
    isLoading,
    error,
    refetch: fetchAnalytics,
  };
}
