import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { authAPI } from '@/lib/api/auth';

export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl: string | null;
  isActive: boolean;
  isSuperuser: boolean;
  createdAt: string;
  updatedAt: string | null;
}

export interface TokenResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface AuthResponse {
  token: TokenResponse;
  user: User;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<AuthResponse | null>;
  register: (name: string, email: string, password: string) => Promise<AuthResponse | null>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        login: async (email: string, password: string) => {
          set({ isLoading: true, error: null });
          try {
            // Proper API authentication flow
            const response = await authAPI.login({ email, password });

            set({
              user: response.user,
              token: response.token.accessToken,
              isAuthenticated: true,
              isLoading: false
            });

            return response;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Login failed',
              isLoading: false
            });
            return null;
          }
        },

        register: async (name: string, email: string, password: string) => {
          set({ isLoading: true, error: null });
          try {
            // Proper API authentication flow
            const response = await authAPI.register({ name, email, password });

            set({
              user: response.user,
              token: response.token.accessToken,
              isAuthenticated: true,
              isLoading: false
            });

            return response;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Registration failed',
              isLoading: false
            });
            return null;
          }
        },

        logout: () => {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            error: null
          });
        },

        setUser: (user: User) => {
          set({ user });
        },

        setToken: (token: string) => {
          set({ token, isAuthenticated: true });
        },

        clearError: () => {
          set({ error: null });
        }
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          user: state.user,
          token: state.token,
          isAuthenticated: state.isAuthenticated
        })
      }
    )
  )
);
