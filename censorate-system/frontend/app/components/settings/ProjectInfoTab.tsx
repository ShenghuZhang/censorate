'use client';

import { useState, useEffect } from 'react';
import { Project } from '@/lib/api/projects';
import { useProjectStore } from '@/app/stores/projectStore';
import LogoUpload from './LogoUpload';
import { Save, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';

interface ProjectInfoTabProps {
  project: Project;
}

export default function ProjectInfoTab({ project }: ProjectInfoTabProps) {
  const { updateProject, isLoading } = useProjectStore();
  const [formData, setFormData] = useState({
    name: project.name,
    description: project.description || '',
    project_type: project.project_type,
    logo_url: project.settings?.logo_url || '',
  });
  const [hasChanges, setHasChanges] = useState(false);

  // 自动生成 slug
  const generateSlug = (name: string) => {
    return name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  };

  useEffect(() => {
    setFormData({
      name: project.name,
      description: project.description || '',
      project_type: project.project_type,
      logo_url: project.settings?.logo_url || '',
    });
  }, [project]);

  useEffect(() => {
    setHasChanges(
      formData.name !== project.name ||
      formData.description !== (project.description || '') ||
      formData.project_type !== project.project_type ||
      formData.logo_url !== (project.settings?.logo_url || '')
    );
  }, [formData, project]);

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleLogoChange = (logoUrl: string) => {
    setFormData(prev => ({ ...prev, logo_url: logoUrl }));
  };

  const handleSave = async () => {
    await updateProject(project.id, {
      name: formData.name,
      description: formData.description,
      settings: {
        ...project.settings,
        logo_url: formData.logo_url,
      },
    });
  };

  return (
    <div className="max-w-3xl">
      <div className="space-y-6">
        {/* Logo Section */}
        <div className="bg-white rounded-lg shadow-soft border border-border p-6">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
            Branding
          </h3>
          <LogoUpload
            currentLogo={formData.logo_url}
            onLogoChange={handleLogoChange}
          />
        </div>

        {/* Form Section */}
        <div className="bg-white rounded-lg shadow-soft border border-border p-6">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
            Project Details
          </h3>

          <div className="space-y-5">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">
                Project Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full px-3.5 py-2.5 bg-surface-soft border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-text-primary text-sm"
                placeholder="Enter project name"
              />
            </div>

            {/* Slug Preview */}
            <div>
              <label className="block text-xs font-medium text-text-muted uppercase tracking-wider mb-1.5">
                Slug
              </label>
              <p className="text-text-secondary font-mono text-xs">{generateSlug(formData.name)}</p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                className="w-full px-3.5 py-2.5 bg-surface-soft border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-text-primary text-sm resize-none"
                placeholder="Enter project description"
              />
            </div>

            {/* Project Type */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-3">
                Project Type
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => handleChange('project_type', 'technical')}
                  className={clsx(
                    'flex items-center gap-2.5 p-3 rounded-lg border-2 transition-all text-left',
                    formData.project_type === 'technical'
                      ? 'border-primary bg-primary-soft'
                      : 'border-border bg-surface-soft hover:border-text-tertiary'
                  )}
                >
                  <div className={clsx(
                    'w-8 h-8 rounded-lg flex items-center justify-center',
                    formData.project_type === 'technical'
                      ? 'bg-gradient-to-br from-purple-500 to-indigo-600'
                      : 'bg-surface-softer'
                  )}>
                    <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                  </div>
                  <div>
                    <div className={clsx(
                      'font-semibold text-sm',
                      formData.project_type === 'technical' ? 'text-text-primary' : 'text-text-secondary'
                    )}>
                      Technical
                    </div>
                    <div className="text-xs text-text-muted">Software dev</div>
                  </div>
                </button>

                <button
                  onClick={() => handleChange('project_type', 'non_technical')}
                  className={clsx(
                    'flex items-center gap-2.5 p-3 rounded-lg border-2 transition-all text-left',
                    formData.project_type === 'non_technical'
                      ? 'border-primary bg-primary-soft'
                      : 'border-border bg-surface-soft hover:border-text-tertiary'
                  )}
                >
                  <div className={clsx(
                    'w-8 h-8 rounded-lg flex items-center justify-center',
                    formData.project_type === 'non_technical'
                      ? 'bg-gradient-to-br from-amber-400 to-orange-500'
                      : 'bg-surface-softer'
                  )}>
                    <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <div className={clsx(
                      'font-semibold text-sm',
                      formData.project_type === 'non_technical' ? 'text-text-primary' : 'text-text-secondary'
                    )}>
                      Business
                    </div>
                    <div className="text-xs text-text-muted">Non-technical</div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={!hasChanges || isLoading}
            className={clsx(
              'inline-flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-all text-sm',
              hasChanges && !isLoading
                ? 'bg-primary text-white hover:bg-primary/90 shadow-soft hover:shadow-medium'
                : 'bg-surface-softer text-text-muted cursor-not-allowed'
            )}
          >
            {isLoading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Save size={16} strokeWidth={2} />
            )}
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}
