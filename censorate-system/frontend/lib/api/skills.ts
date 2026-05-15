// frontend/lib/api/skills.ts
import { api } from './client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8216/api/v1';

export interface SkillFile {
    id: string;
    path: string;
    file_size: number;
}

export interface SkillVersion {
    id: string;
    version: string;
    changelog?: string;
    is_latest: boolean;
    created_at: string;
    files?: SkillFile[];
}

export interface Skill {
    id: string;
    name: string;
    slug: string;
    description?: string;
    category: string;
    tags: string[];
    created_at: string;
    updated_at?: string;
    latest_version?: SkillVersion;
    versions?: SkillVersion[];
    stats?: {
        downloads: number;
        views: number;
    };
}

export const skillsAPI = {
    listSkills: () => api.get<{ skills: Skill[] }>('/skills'),
    getSkill: (slug: string) => api.get<Skill>(`/skills/${slug}`),
    getCategories: () => api.get<{ categories: string[] }>('/skills/categories'),
    uploadSkill: async (files: File[], metadata: any) => {
        const formData = new FormData();
        files.forEach(f => formData.append('files', f));
        formData.append('metadata', JSON.stringify(metadata));
        let token = null;
        try {
            const s = localStorage.getItem('auth-storage');
            if (s) token = JSON.parse(s).state.token;
        } catch {}
        const res = await fetch(`${API_URL}/skills`, {
            method: 'POST',
            body: formData,
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'Upload failed');
        return res.json();
    },
    downloadSkill: async (slug: string, version?: string | null): Promise<Blob> => {
        const url = version
            ? `${API_URL}/skills/${slug}/download?version=${version}`
            : `${API_URL}/skills/${slug}/download`;
        let token = null;
        try {
            const s = localStorage.getItem('auth-storage');
            if (s) token = JSON.parse(s).state.token;
        } catch {}
        const res = await fetch(url, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!res.ok) throw new Error('Download failed');
        return res.blob();
    },
    getFileContent: async (slug: string, filename: string, version?: string | null): Promise<string> => {
        const url = version
            ? `${API_URL}/skills/${slug}/files/${filename}?version=${version}`
            : `${API_URL}/skills/${slug}/files/${filename}`;
        let token = null;
        try {
            const s = localStorage.getItem('auth-storage');
            if (s) token = JSON.parse(s).state.token;
        } catch {}
        const res = await fetch(url, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!res.ok) throw new Error('Failed to load file');
        return res.text();
    },
    archiveSkill: (slug: string) => api.delete(`/skills/${slug}`),
    deleteSkillPermanently: (slug: string) => api.delete(`/skills/${slug}/permanent`),
};
