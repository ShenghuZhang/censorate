'use client';

import { useEffect } from 'react';
import { useAuthStore } from './stores/authStore';
import { api } from '@/lib/api/client';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { token, logout } = useAuthStore();

  // Initialize API client
  useEffect(() => {
    if (token) {
      api.setToken(token);
    }
    api.setOnUnauthorized(() => {
      logout();
    });
  }, [token, logout]);

  return <>{children}</>;
}
