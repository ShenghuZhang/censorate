'use client';

import Layout from '@/app/components/layout/Layout';

export default function BacklogPage() {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Backlog</h1>
            <p className="text-gray-600 mt-2">Manage your requirement backlog</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">Backlog functionality coming soon...</p>
        </div>
      </div>
    </Layout>
  );
}
