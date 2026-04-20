'use client';

import { useState, useEffect } from 'react';
import Layout from '@/app/components/layout/Layout';
import ProjectInfoTab from '@/app/components/settings/ProjectInfoTab';
import MembersTab from '@/app/components/settings/MembersTab';
import { useProjectStore } from '@/app/stores/projectStore';
import { Settings as SettingsIcon, Users, FolderKanban } from 'lucide-react';
import { clsx } from 'clsx';

type TabType = 'project' | 'members';

export default function SettingsPage() {
  const { currentProject } = useProjectStore();
  const [activeTab, setActiveTab] = useState<TabType>('project');

  const tabs = [
    {
      id: 'project' as TabType,
      label: 'Project Info',
      icon: FolderKanban,
    },
    {
      id: 'members' as TabType,
      label: 'Members',
      icon: Users,
    },
  ];

  if (!currentProject) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
                <SettingsIcon size={24} className="text-primary" />
                Settings
              </h1>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-soft border border-border p-10 text-center">
            <div className="w-14 h-14 bg-surface-soft rounded-2xl flex items-center justify-center mx-auto mb-3">
              <SettingsIcon size={28} className="text-text-muted" />
            </div>
            <h3 className="text-base font-semibold text-text-primary mb-2">
              Select a Project
            </h3>
            <p className="text-text-muted text-sm">
              Choose a project from the header to view settings
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <SettingsIcon size={24} className="text-primary" />
            <h1 className="text-2xl font-bold text-text-primary">
              Settings
            </h1>
          </div>
          <p className="text-text-muted text-sm mt-1">
            Manage your project configuration
            {currentProject && (
              <span className="text-text-tertiary ml-2">
                for {currentProject.name}
              </span>
            )}
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="flex items-center gap-1.5 bg-surface-soft p-1.5 rounded-xl w-fit">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={clsx(
                    'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
                    isActive
                      ? 'bg-white text-text-primary shadow-soft'
                      : 'text-text-secondary hover:text-text-primary'
                  )}
                >
                  <Icon size={16} strokeWidth={isActive ? 2 : 1.5} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="min-h-[400px]">
          {activeTab === 'project' && (
            <ProjectInfoTab project={currentProject} />
          )}
          {activeTab === 'members' && (
            <MembersTab />
          )}
        </div>
      </div>
    </Layout>
  );
}
