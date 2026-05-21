'use client';

import { useState, useEffect, FormEvent } from 'react';
import { useGenerationProjectStore } from '@/app/stores/generationProjectStore';
import { useTemplateStore } from '@/app/stores/templateStore';
import { useRouter } from 'next/navigation';

export default function NewProjectForm() {
  const router = useRouter();
  const { createProject, isLoading } = useGenerationProjectStore();
  const { templates, fetchTemplates } = useTemplateStore();
  const [name, setName] = useState('');
  const [userStory, setUserStory] = useState('');
  const [templateSlug, setTemplateSlug] = useState('fastapi-nextjs');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim() || !userStory.trim()) {
      setError('Project name and user story are required');
      return;
    }

    const project = await createProject({
      name: name.trim(),
      user_story: userStory.trim(),
      template_slug: templateSlug,
    });

    if (project) {
      router.push(`/projects/${project.id}`);
    } else {
      setError('Failed to create project');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Project Name
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., My E-commerce API"
          className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-sm"
        />
      </div>

      <div>
        <label htmlFor="template" className="block text-sm font-medium text-gray-700 mb-1">
          Template
        </label>
        <select
          id="template"
          value={templateSlug}
          onChange={(e) => setTemplateSlug(e.target.value)}
          className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-sm"
        >
          {templates.map((t) => (
            <option key={t.slug} value={t.slug}>
              {t.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="userStory" className="block text-sm font-medium text-gray-700 mb-1">
          User Story / Requirements
        </label>
        <textarea
          id="userStory"
          value={userStory}
          onChange={(e) => setUserStory(e.target.value)}
          placeholder="Describe what you want to build. Be as detailed as possible..."
          rows={8}
          className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-sm resize-y"
        />
        <p className="mt-1 text-xs text-gray-500">
          Describe your idea in detail: what problem it solves, key features, target users, etc.
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-colors text-sm"
      >
        {isLoading ? 'Creating...' : 'Generate Code'}
      </button>
    </form>
  );
}
