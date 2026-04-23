'use client';

import { useState, useEffect } from 'react';
import Layout from '@/app/components/layout/Layout';
import ProjectInfoTab from '@/app/components/settings/ProjectInfoTab';
import MembersTab from '@/app/components/settings/MembersTab';
import RepositoriesTab from '@/app/components/settings/RepositoriesTab';
import { useProjectStore } from '@/app/stores/projectStore';
import { Settings as SettingsIcon, Users, FolderKanban, GitBranch } from 'lucide-react';
import { clsx } from 'clsx';

type TabType = 'project' | 'members' | 'repositories';

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
    {
      id: 'repositories' as TabType,
      label: 'Repositories',
      icon: GitBranch,
    },
  ];

  if (!currentProject) {
    return (
      <Layout>
        <div className="max-w-5xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-2xl font-semibold text-text-primary flex items-center gap-3">
                <SettingsIcon size={24} className="text-text-muted" />
                Settings
              </h1>
            </div>
          </div>
          <div className="bg-surface-soft border border-border rounded-2xl p-12 text-center shadow-soft">
            <div className="w-16 h-16 bg-surface-softer border border-border rounded-2xl flex items-center justify-center mx-auto mb-4">
              <SettingsIcon size={32} className="text-text-muted" />
            </div>
            <h3 className="text-lg font-medium text-text-secondary mb-2">
              Select a Project
            </h3>
            <p className="text-text-tertiary text-sm">
              Choose a project from the header to view settings
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <SettingsIcon size={24} className="text-text-muted" />
            <h1 className="text-2xl font-semibold text-text-primary">
              Settings
            </h1>
          </div>
          <p className="text-text-tertiary text-sm mt-1">
            Manage your project configuration
            {currentProject && (
              <span className="text-text-muted ml-2">
                for {currentProject.name}
              </span>
            )}
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex items-center gap-1.5 bg-surface-soft border border-border p-1.5 rounded-2xl w-fit shadow-soft">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={clsx(
                    'flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-surface text-text-secondary shadow-medium border border-border'
                      : 'text-text-tertiary hover:text-text-secondary hover:bg-surface-softer'
                  )}
                >
                  <Icon size={17} strokeWidth={isActive ? 2 : 1.7} />
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
          {activeTab === 'repositories' && (
            <RepositoriesTab />
          )}
        </div>
      </div>
    </Layout>
  );
}
