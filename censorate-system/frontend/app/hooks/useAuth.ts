import { useAuthStore } from '../stores/authStore';

export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    setUser,
    setToken,
    clearError
  } = useAuthStore();

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    setUser,
    setToken,
    clearError
  };
};

export const useRequireAuth = (redirectTo: string = '/login') => {
  const { isAuthenticated } = useAuth();

  if (typeof window !== 'undefined') {
    if (!isAuthenticated) {
      // In a real app, we would redirect here
      // But for now, just return false
      return false;
    }
  }

  return true;
};

export const useCurrentUser = () => {
  const { user } = useAuth();
  return user;
};
