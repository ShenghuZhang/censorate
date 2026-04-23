'use client';

import { useState, useEffect } from 'react';
import { Project } from '@/lib/api/projects';
import { useProjectStore } from '@/app/stores/projectStore';
import LogoUpload from './LogoUpload';
import SwimlaneSelector, { DEFAULT_LANES } from './SwimlaneSelector';
import EmojiPicker from '@/app/components/projects/EmojiPicker';
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
    emoji: project.settings?.emoji || '',
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
      emoji: project.settings?.emoji || '',
      swimlanes: project.settings?.swimlanes || DEFAULT_LANES,
    });
  }, [project]);

  useEffect(() => {
    setHasChanges(
      formData.name !== project.name ||
      formData.description !== (project.description || '') ||
      formData.logo_url !== (project.settings?.logo_url || '') ||
      formData.emoji !== (project.settings?.emoji || '') ||
      JSON.stringify(formData.swimlanes) !== JSON.stringify(project.settings?.swimlanes || DEFAULT_LANES)
    );
  }, [formData, project]);

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleLogoChange = (logoUrl: string) => {
    setFormData(prev => ({ ...prev, logo_url: logoUrl }));
  };

  const handleEmojiChange = (emoji: string) => {
    setFormData(prev => ({ ...prev, emoji }));
  };

  const handleSave = async () => {
    await updateProject(project.id, {
      name: formData.name,
      description: formData.description,
      settings: {
        ...project.settings,
        logo_url: formData.logo_url,
        emoji: formData.emoji,
        swimlanes: formData.swimlanes,
      },
    });
  };

  return (
    <div className="max-w-3xl">
      <div className="space-y-8">
        {/* Branding Section */}
        <div className="border-b border-gray-200 pb-8">
          <h3 className="text-sm font-semibold text-gray-900 mb-6">
            Branding
          </h3>
          <div className="flex items-start gap-8">
            <div className="flex flex-col gap-3">
              <label className="text-sm font-medium text-gray-700">Icon</label>
              <EmojiPicker value={formData.emoji} onChange={handleEmojiChange} />
              <p className="text-xs text-gray-500">
                Used as project icon and browser tab
              </p>
            </div>
            <div className="flex-1">
              <LogoUpload
                currentLogo={formData.logo_url}
                onLogoChange={handleLogoChange}
              />
            </div>
          </div>
        </div>

        {/* Project Details Section */}
        <div className="border-b border-gray-200 pb-8">
          <h3 className="text-sm font-semibold text-gray-900 mb-6">
            Project Details
          </h3>

          <div className="space-y-5">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition-all text-sm text-gray-900 placeholder:text-gray-400"
                placeholder="Enter project name"
              />
            </div>

            {/* Slug Preview */}
            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                Slug
              </label>
              <p className="text-gray-600 font-mono text-xs bg-gray-50 px-3 py-2 rounded-md border border-gray-200 w-fit">
                {generateSlug(formData.name)}
              </p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition-all text-sm text-gray-900 placeholder:text-gray-400 resize-none"
                placeholder="Enter project description"
              />
            </div>
          </div>
        </div>

        {/* Swimlane Configuration */}
        <div className="border-b border-gray-200 pb-8">
          <SwimlaneSelector
            value={formData.swimlanes}
            onChange={(lanes) => setFormData(prev => ({ ...prev, swimlanes: lanes }))}
          />
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-4">
          <button
            onClick={handleSave}
            disabled={!hasChanges || isLoading}
            className={clsx(
              'inline-flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all',
              hasChanges && !isLoading
                ? 'bg-green-600 text-white hover:bg-green-700 hover:shadow-sm'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            )}
          >
            {isLoading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Save size={16} strokeWidth={2} />
            )}
            {isLoading ? 'Saving...' : 'Save changes'}
          </button>
        </div>
      </div>
    </div>
  );
}
