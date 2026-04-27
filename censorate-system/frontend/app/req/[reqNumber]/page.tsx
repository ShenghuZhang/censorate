'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { useRequirementStore } from '@/app/stores/requirementStore';

export default function ReqNumberPage() {
  const params = useParams();
  const router = useRouter();
  const { requirements, fetchRequirements, isLoading } = useRequirementStore();

  useEffect(() => {
    if (requirements.length === 0) {
      fetchRequirements();
    }
  }, [fetchRequirements, requirements.length]);

  useEffect(() => {
    if (requirements.length > 0 && params.reqNumber) {
      const reqNumber = parseInt(params.reqNumber as string);
      const req = requirements.find((r: any) => r.reqNumber === reqNumber);
      if (req) {
        router.replace(`/requirements/${req.id}`);
      }
    }
  }, [requirements, params.reqNumber, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="flex items-center gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        <span className="text-gray-500">Redirecting...</span>
      </div>
    </div>
  );
}
