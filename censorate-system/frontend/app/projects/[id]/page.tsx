'use client';

import { useAuth } from '@/app/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useParams } from 'next/navigation';
import Layout from '@/app/components/layout/Layout';
import ProjectDetail from '@/app/components/generation/ProjectDetail';

export default function ProjectPage() {
  const router = useRouter();
  const params = useParams();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  return (
    <Layout>
      <ProjectDetail projectId={params.id as string} />
    </Layout>
  );
}
