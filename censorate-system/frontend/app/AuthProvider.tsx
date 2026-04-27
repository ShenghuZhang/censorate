'use client';

import { useEffect, useRef } from 'react';
import { useAuthStore } from './stores/authStore';
import { api } from '@/lib/api/client';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { token, login, isAuthenticated, isLoading, logout } = useAuthStore();
  const hasAutoLoggedIn = useRef(false);
  const isInitialMount = useRef(true);

  // Validate stored auth on mount
  useEffect(() => {
    const validateAuth = async () => {
      if (isInitialMount.current) {
        isInitialMount.current = false;

        // Check if we have a stored user that might be invalid
        const storedAuth = localStorage.getItem('auth-storage');
        if (storedAuth) {
          try {
            const parsed = JSON.parse(storedAuth);
            // If we have a token but no user, or invalid user data, clear it
            if (!parsed.state?.user || !parsed.state?.token) {
              console.log('Clearing invalid auth data');
              logout();
            }
          } catch (e) {
            console.log('Clearing corrupted auth data');
            logout();
          }
        }
      }
    };

    validateAuth();
  }, [logout]);

  // Initialize API client
  useEffect(() => {
    if (token) {
      api.setToken(token);
    }
    api.setOnUnauthorized(() => {
      // Don't logout on unauthorized since we have auto-login
    });
  }, [token]);

  return <>{children}</>;
}
