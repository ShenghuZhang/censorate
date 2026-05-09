// frontend/lib/api/auth.ts
import { api } from './client';

export const authAPI = {
  login: async (credentials: any) => {
    // Standard OAuth2 password flow: login endpoint returns token and user
    // Note: If your backend uses form-data for login, this should be adjusted.
    // Based on authStore, it expects { token: { accessToken }, user: { ... } }
    return api.post<any>('/auth/login', credentials);
  },
  register: async (data: any) => {
    return api.post<any>('/auth/register', data);
  },
  getMe: async () => {
    return api.get<any>('/auth/me');
  }
};
