'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { Requirement, useRequirementStore } from '@/app/stores/requirementStore';
import { requirementsAPI } from '@/lib/api/requirements';
import RequirementDetail from '@/app/components/requirement/RequirementDetail';

export default function RequirementPage() {
  const params = useParams();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { fetchComments, fetchHistory, selectedRequirement, setSelectedRequirement } = useRequirementStore();
  const requirement = selectedRequirement;

  useEffect(() => {
    const fetchRequirement = async () => {
      if (!params.requirementId) return;

      try {
        setIsLoading(true);
        setError(null);
        const req = await requirementsAPI.getRequirement(params.requirementId as string);
        setSelectedRequirement(req);

        // Fetch comments and history
        await fetchComments(req.id);
        await fetchHistory(req.id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch requirement');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRequirement();
  }, [params.requirementId, fetchComments, fetchHistory, setSelectedRequirement]);

  const handleBack = () => {
    router.back();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-3">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
          <span className="text-gray-500">Loading...</span>
        </div>
      </div>
    );
  }

  if (error || !requirement) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-gray-500">{error || 'Requirement not found'}</p>
        <button
          onClick={handleBack}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <ArrowLeft size={16} />
          Back
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back button header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 sticky top-0 z-20">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 rounded-xl transition-colors"
        >
          <ArrowLeft size={20} className="text-gray-600" />
          <span className="text-sm font-medium text-gray-600">Back</span>
        </button>
      </div>

      {/* Requirement detail in page mode */}
      <RequirementDetail requirement={requirement} mode="page" />
    </div>
  );
}
