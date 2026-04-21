'use client';

import { useState, useEffect } from 'react';
import { Project } from '@/lib/api/projects';
import { useProjectStore } from '@/app/stores/projectStore';
import LogoUpload from './LogoUpload';
import SwimlaneSelector, { DEFAULT_LANES } from './SwimlaneSelector';
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
    logo_url: project.settings?.logo_url || '',
    swimlanes: project.settings?.swimlanes || DEFAULT_LANES,
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
      logo_url: project.settings?.logo_url || '',
      swimlanes: project.settings?.swimlanes || DEFAULT_LANES,
    });
  }, [project]);

  useEffect(() => {
    setHasChanges(
      formData.name !== project.name ||
      formData.description !== (project.description || '') ||
      formData.logo_url !== (project.settings?.logo_url || '') ||
      JSON.stringify(formData.swimlanes) !== JSON.stringify(project.settings?.swimlanes || DEFAULT_LANES)
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
        swimlanes: formData.swimlanes,
      },
    });
  };

  return (
    <div className="max-w-3xl">
      <div className="space-y-5">
        {/* Logo Section */}
        <div className="bg-slate-50/70 border border-slate-200/60 rounded-2xl p-6 shadow-sm">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
            Branding
          </h3>
          <LogoUpload
            currentLogo={formData.logo_url}
            onLogoChange={handleLogoChange}
          />
        </div>

        {/* Form Section */}
        <div className="bg-slate-50/70 border border-slate-200/60 rounded-2xl p-6 shadow-sm">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-5">
            Project Details
          </h3>

          <div className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">
                Project Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-300 focus:border-slate-400 outline-none transition-all duration-200 text-slate-700 text-sm shadow-sm"
                placeholder="Enter project name"
              />
            </div>

            {/* Slug Preview */}
            <div>
              <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                Slug
              </label>
              <p className="text-slate-500 font-mono text-xs bg-white/70 px-3 py-1.5 rounded-lg border border-slate-100 w-fit">
                {generateSlug(formData.name)}
              </p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-300 focus:border-slate-400 outline-none transition-all duration-200 text-slate-700 text-sm resize-none shadow-sm"
                placeholder="Enter project description"
              />
            </div>
          </div>
        </div>

        {/* Swimlane Configuration */}
        <div className="bg-slate-50/70 border border-slate-200/60 rounded-2xl p-6 shadow-sm">
          <SwimlaneSelector
            value={formData.swimlanes}
            onChange={(lanes) => setFormData(prev => ({ ...prev, swimlanes: lanes }))}
          />
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-2">
          <button
            onClick={handleSave}
            disabled={!hasChanges || isLoading}
            className={clsx(
              'inline-flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all text-sm duration-200',
              hasChanges && !isLoading
                ? 'bg-slate-600 text-white hover:bg-slate-700 shadow-md hover:shadow-lg'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            )}
          >
            {isLoading ? (
              <Loader2 size={17} className="animate-spin" />
            ) : (
              <Save size={17} strokeWidth={2} />
            )}
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}
