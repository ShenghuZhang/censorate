'use client';

import Layout from '@/app/components/layout/Layout';
import StatusOverview from '@/app/components/analytics/StatusOverview';
import ThroughputChart from '@/app/components/analytics/ThroughputChart';
import WorkloadChart from '@/app/components/analytics/WorkloadChart';
import { useProjectStore } from '@/app/stores/projectStore';
import { useAnalytics } from '@/app/hooks/useAnalytics';
import { BarChart3, Loader2, AlertCircle } from 'lucide-react';

export default function AnalyticsPage() {
  const { currentProject } = useProjectStore();
  const { statusStats, dailyThroughput, memberWorkload, totalRequirements, isLoading, error, refetch } = useAnalytics(
    currentProject?.id || null
  );

  if (isLoading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-text-primary flex items-center gap-3">
                <BarChart3 size={28} className="text-primary" />
                Analytics
              </h1>
            </div>
          </div>
          <div className="flex items-center justify-center h-64">
            <Loader2 size={40} className="text-primary animate-spin" />
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-text-primary flex items-center gap-3">
                <BarChart3 size={28} className="text-primary" />
                Analytics
              </h1>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-soft border border-border p-12 text-center">
            <div className="w-16 h-16 bg-red-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <AlertCircle size={32} className="text-red-500" />
            </div>
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              Failed to Load Analytics
            </h3>
            <p className="text-text-muted mb-4">{error}</p>
            <button
              onClick={refetch}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-text-primary flex items-center gap-3">
              <BarChart3 size={28} className="text-primary" />
              Analytics
            </h1>
            <p className="text-text-muted mt-2">
              View project analytics and insights
              {currentProject && (
                <span className="text-text-tertiary ml-2">
                  for {currentProject.name}
                </span>
              )}
            </p>
          </div>
        </div>

        {currentProject ? (
          <>
            <StatusOverview stats={statusStats} total={totalRequirements} />
            <ThroughputChart data={dailyThroughput} />
            <WorkloadChart data={memberWorkload} />
          </>
        ) : (
          <div className="bg-white rounded-lg shadow-soft border border-border p-12 text-center">
            <div className="w-16 h-16 bg-surface-soft rounded-2xl flex items-center justify-center mx-auto mb-4">
              <BarChart3 size={32} className="text-text-muted" />
            </div>
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              Select a Project
            </h3>
            <p className="text-text-muted">
              Choose a project from the header to view analytics
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
