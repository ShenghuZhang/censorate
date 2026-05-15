'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Layout from '@/app/components/layout/Layout';
import {
  Brain,
  Plus,
  Search,
  Upload,
  RefreshCw,
  Eye,
  Filter,
  Download,
  Clock,
  Star,
  ArrowDownToLine,
  X,
  FileText,
  ExternalLink
} from 'lucide-react';
import { skillsAPI, type Skill } from '@/lib/api/skills';
import { clsx } from 'clsx';

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [uploadMetadata, setUploadMetadata] = useState({
    name: '',
    description: '',
    category: 'custom',
    tags: [] as string[],
    version: '1.0.0',
    changelog: ''
  });
  const [isUploading, setIsUploading] = useState(false);
  const [sortBy, setSortBy] = useState<'latest' | 'popular'>('latest');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [skillsRes, categoriesRes] = await Promise.all([
        skillsAPI.listSkills(),
        skillsAPI.getCategories(),
      ]);
      setSkills(skillsRes.skills);
      setCategories(categoriesRes.categories);
    } catch (error) {
      console.error('Failed to load skills:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReload = async () => {
    await loadData();
  };

  const handleUpload = async () => {
    if (uploadFiles.length === 0 || !uploadMetadata.name) return;

    setIsUploading(true);
    try {
      await skillsAPI.uploadSkill(uploadFiles, uploadMetadata);
      setShowUpload(false);
      setUploadFiles([]);
      setUploadMetadata({
        name: '',
        description: '',
        category: 'custom',
        tags: [],
        version: '1.0.0',
        changelog: ''
      });
      await loadData();
    } catch (error) {
      console.error('Failed to upload skill:', error);
      alert(error instanceof Error ? error.message : 'Failed to upload skill');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = async (skill: Skill, version?: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      const blob = await skillsAPI.downloadSkill(skill.slug, version);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const versionStr = version || skill.latest_version?.version || 'latest';
      a.download = `${skill.slug}-${versionStr}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download skill:', error);
      alert('Failed to download skill');
    }
  };

  const handleCardClick = (skill: Skill) => {
    window.open(`/skills/${skill.slug}`, '_blank');
  };

  const filteredSkills = skills.filter(skill => {
    const matchesSearch =
      !searchQuery ||
      skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (skill.description?.toLowerCase() || '').includes(searchQuery.toLowerCase());

    const matchesCategory =
      selectedCategory === 'all' || skill.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // Sort skills
  const sortedSkills = [...filteredSkills].sort((a, b) => {
    if (sortBy === 'latest') {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    } else {
      // Sort by downloads (if available)
      const aDownloads = a.stats?.downloads || 0;
      const bDownloads = b.stats?.downloads || 0;
      return bDownloads - aDownloads;
    }
  });

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Brain size={22} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Skills</h1>
          </div>
          <p className="text-gray-600 text-base">
            Manage and browse AI agent skills for your projects
          </p>
        </div>

        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6 items-start sm:items-center justify-between">
          {/* Search */}
          <div className="flex-1 w-full sm:w-auto">
            <div className="relative">
              <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search skills..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full sm:w-80 pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-gray-900 text-base"
              />
            </div>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            {/* Sort */}
            <div className="flex items-center gap-1 bg-gray-100 rounded-xl p-1.5">
              <button
                onClick={() => setSortBy('latest')}
                className={clsx(
                  'px-4 py-2 rounded-lg text-sm font-semibold transition-all',
                  sortBy === 'latest'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-900'
                )}
              >
                <div className="flex items-center gap-1.5">
                  <Clock size={15} />
                  Latest
                </div>
              </button>
              <button
                onClick={() => setSortBy('popular')}
                className={clsx(
                  'px-4 py-2 rounded-lg text-sm font-semibold transition-all',
                  sortBy === 'popular'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-900'
                )}
              >
                <div className="flex items-center gap-1.5">
                  <Star size={15} />
                  Popular
                </div>
              </button>
            </div>

            {/* Category Filter */}
            <div className="flex items-center gap-1 bg-gray-100 rounded-xl p-1.5">
              <button
                onClick={() => setSelectedCategory('all')}
                className={clsx(
                  'px-4 py-2 rounded-lg text-sm font-semibold transition-all',
                  selectedCategory === 'all'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-900'
                )}
              >
                All
              </button>
              {categories.slice(0, 3).map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={clsx(
                    'px-4 py-2 rounded-lg text-sm font-semibold transition-all',
                    selectedCategory === category
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-500 hover:text-gray-900'
                  )}
                >
                  {category}
                </button>
              ))}
            </div>

            {/* Actions */}
            <button
              onClick={handleReload}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-all font-medium text-sm"
            >
              <RefreshCw size={17} />
              Reload
            </button>

            <button
              onClick={() => setShowUpload(true)}
              className="inline-flex items-center gap-2.5 px-5 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all font-medium text-sm shadow-sm shadow-blue-600/20"
            >
              <Plus size={17} />
              Upload Skill
            </button>
          </div>
        </div>

        {/* Skills Grid */}
        {isLoading ? (
          <div className="flex justify-center py-14">
            <div className="animate-spin w-7 h-7 border-2 border-gray-200 rounded-full border-t-blue-600" />
          </div>
        ) : sortedSkills.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-10 text-center">
            <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
              <Filter size={28} className="text-gray-400" />
            </div>
            <h3 className="text-base font-semibold text-gray-900 mb-2">
              No skills found
            </h3>
            <p className="text-gray-500 text-sm">
              {searchQuery || selectedCategory !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Start by uploading a skill'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {sortedSkills.map((skill) => (
              <div
                key={skill.id}
                onClick={() => handleCardClick(skill)}
                className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow-lg hover:border-gray-300 transition-all cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-5">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
                      <Brain size={24} className="text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-gray-900 text-lg truncate group-hover:text-blue-600 transition-colors">{skill.name}</h3>
                      <div className="flex items-center gap-2 mt-1.5">
                        <span className="text-xs bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded-full font-medium">
                          {skill.category}
                        </span>
                        {skill.latest_version && (
                          <span className="text-xs text-gray-400 font-medium">
                            v{skill.latest_version.version}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="w-8 h-8 bg-gray-50 rounded-lg flex items-center justify-center group-hover:bg-blue-50 transition-colors">
                    <ExternalLink size={16} className="text-gray-400 group-hover:text-blue-600 transition-colors" />
                  </div>
                </div>

                <p className="text-sm text-gray-600 line-clamp-2 mb-5 min-h-[40px]">
                  {skill.description || 'No description available'}
                </p>

                {/* Tags */}
                {skill.tags?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-5">
                    {skill.tags.slice(0, 3).map((tag, i) => (
                      <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full font-medium">
                        {tag}
                      </span>
                    ))}
                    {skill.tags.length > 3 && (
                      <span className="text-xs text-gray-400 font-medium">
                        +{skill.tags.length - 3} more
                      </span>
                    )}
                  </div>
                )}

                {/* Stats */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="flex items-center gap-5">
                    <div className="flex items-center gap-1.5 text-gray-500 text-xs">
                      <Download size={14} />
                      <span className="font-semibold">{skill.stats?.downloads || 0}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-gray-500 text-xs">
                      <Eye size={14} />
                      <span className="font-semibold">{skill.stats?.views || 0}</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDownload(skill, undefined, e)}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-all text-xs font-semibold group-hover:bg-blue-600"
                  >
                    <ArrowDownToLine size={13} />
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Upload Dialog */}
        {showUpload && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setShowUpload(false)} />
            <div className="relative bg-white rounded-xl shadow-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-start justify-between">
                  <h2 className="text-lg font-bold text-gray-900">Upload Skill</h2>
                  <button
                    onClick={() => setShowUpload(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X size={20} />
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-4">
                {/* Metadata */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Skill Name *
                  </label>
                  <input
                    type="text"
                    value={uploadMetadata.name}
                    onChange={(e) => setUploadMetadata({ ...uploadMetadata, name: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    placeholder="My awesome skill"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Description
                  </label>
                  <textarea
                    value={uploadMetadata.description}
                    onChange={(e) => setUploadMetadata({ ...uploadMetadata, description: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    rows={3}
                    placeholder="What does this skill do?"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Category *
                    </label>
                    <select
                      value={uploadMetadata.category}
                      onChange={(e) => setUploadMetadata({ ...uploadMetadata, category: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    >
                      {Array.from(new Set(['custom', 'analysis', 'design', 'development', 'testing', ...categories])).map((cat) => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Version
                    </label>
                    <input
                      type="text"
                      value={uploadMetadata.version}
                      onChange={(e) => setUploadMetadata({ ...uploadMetadata, version: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                      placeholder="1.0.0"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Tags
                  </label>
                  <input
                    type="text"
                    placeholder="comma separated"
                    onChange={(e) => setUploadMetadata({
                      ...uploadMetadata,
                      tags: e.target.value.split(',').map(t => t.trim()).filter(t => t)
                    })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Changelog
                  </label>
                  <textarea
                    value={uploadMetadata.changelog}
                    onChange={(e) => setUploadMetadata({ ...uploadMetadata, changelog: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                    rows={2}
                    placeholder="What changed in this version?"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Skill Files (.md, .json, .py, .zip, etc.) *
                  </label>
                  <div
                    onClick={() => document.getElementById('skill-files')?.click()}
                    className="border-2 border-dashed border-gray-200 rounded-lg p-8 text-center cursor-pointer hover:border-gray-300"
                  >
                    <Upload size={32} className="mx-auto mb-2 text-gray-400" />
                    <p className="text-sm text-gray-600">
                      {uploadFiles.length > 0
                        ? `${uploadFiles.length} file(s) selected`
                        : 'Click to select or drag files'}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      SKILL.md is required
                    </p>
                    <input
                      id="skill-files"
                      type="file"
                      multiple
                      accept=".md,.json,.yaml,.yml,.txt,.py,.js,.ts,.tsx,.jsx,.sh,.css,.html,.xml,.csv,.ini,.cfg,.conf,.toml,.env,.go,.rs,.java,.kt,.scala,.php,.rb,.cpp,.c,.h,.cs,.fs,.sql,.graphql,.gql,.lua,.pl,.r,.dart,.swift,.zip"
                      onChange={(e) => setUploadFiles(Array.from(e.target.files || []))}
                      className="hidden"
                    />
                  </div>
                  {uploadFiles.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {uploadFiles.map((file, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                          <FileText size={14} />
                          <span className="truncate">{file.name}</span>
                          <span className="text-gray-400 text-xs">({(file.size / 1024).toFixed(1)} KB)</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-end gap-3 p-6 border-t border-gray-100">
                <button
                  onClick={() => setShowUpload(false)}
                  className="px-4 py-2.5 text-gray-600 hover:text-gray-900 font-medium text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={!uploadMetadata.name || uploadFiles.length === 0 || isUploading}
                  className="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium text-sm"
                >
                  {isUploading ? 'Uploading...' : 'Upload Skill'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
