import { api } from './client';

export interface Attachment {
  id: string;
  requirementId: string;
  filename: string;
  contentType: string;
  size: number;
  url?: string;
  storageKey: string;
  uploadedBy?: string;
  createdAt: string;
}

export const attachmentsApi = {
  uploadAttachment: async (requirementId: string, file: File): Promise<Attachment> => {
    const formData = new FormData();
    formData.append('file', file);

    let token: string | null = null;
    try {
      const s = localStorage.getItem('auth-storage');
      if (s) token = JSON.parse(s).state.token;
    } catch {}

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8216/api/v1';
    const response = await fetch(
      `${API_BASE_URL}/requirements/${requirementId}/attachments`,
      {
        method: 'POST',
        body: formData,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail));
    }

    return response.json();
  },

  getAttachments: (requirementId: string): Promise<Attachment[]> =>
    api.get<Attachment[]>(`/requirements/${requirementId}/attachments`),

  deleteAttachment: (requirementId: string, attachmentId: string): Promise<void> =>
    api.delete<void>(`/requirements/${requirementId}/attachments/${attachmentId}`),
};
