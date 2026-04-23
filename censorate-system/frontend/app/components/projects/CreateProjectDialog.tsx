'use client';

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import SwimlaneSelector, { DEFAULT_LANES } from '@/app/components/settings/SwimlaneSelector';
import EmojiPicker from './EmojiPicker';

interface CreateProjectDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  isLoading: boolean;
  editProject?: any;
}

export default function CreateProjectDialog({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
  editProject
}: CreateProjectDialogProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [swimlanes, setSwimlanes] = useState<string[]>(DEFAULT_LANES);
  const [emoji, setEmoji] = useState('');

  useEffect(() => {
    if (editProject) {
      setName(editProject.name);
      setDescription(editProject.description || '');
      setSwimlanes(editProject.settings?.swimlanes || DEFAULT_LANES);
      setEmoji(editProject.settings?.emoji || '');
    } else if (isOpen) {
      setName('');
      setDescription('');
      setSwimlanes(DEFAULT_LANES);
      setEmoji('');
    }
  }, [editProject, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      name,
      description,
      project_type: 'non_technical',
      settings: { swimlanes, emoji }
    });
  };

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-8 border border-slate-200">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-slate-900 tracking-tight">
            {editProject ? 'Edit Project' : 'New Project'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="flex items-start gap-4">
            <div className="flex flex-col items-center gap-2">
              <label className="block text-sm font-medium text-slate-700">Icon</label>
              <EmojiPicker value={emoji} onChange={setEmoji} />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                Project Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-slate-300 focus:border-slate-400 outline-none transition-all text-sm"
                placeholder="Enter project name"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-50/80 border border-slate-200/80 rounded-xl focus:ring-2 focus:ring-slate-300 focus:border-slate-400 outline-none transition-all text-sm resize-none"
              rows={3}
              placeholder="Enter project description"
            />
          </div>

          <SwimlaneSelector value={swimlanes} onChange={setSwimlanes} />

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-5 py-2.5 text-slate-600 hover:text-slate-900 font-medium text-sm transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !name}
              className="flex-1 px-5 py-2.5 bg-slate-600 text-white rounded-xl hover:bg-slate-700 transition-all font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-sm shadow-slate-500/25"
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {editProject ? 'Saving...' : 'Creating...'}
                </div>
              ) : (
                editProject ? 'Save Changes' : 'Create Project'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
