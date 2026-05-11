// frontend/lib/api/client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8216/api/v1';

let token: string | null = null;
let onUnauthorizedCallback: (() => void) | null = null;

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  // Use in-memory token first, fallback to localStorage
  let currentToken = token;
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage && !currentToken) {
      currentToken = JSON.parse(authStorage).state.token;
    }
  } catch (e) {
    // localStorage may not be available in SSR context
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(currentToken ? { 'Authorization': `Bearer ${currentToken}` } : {}),
    ...(options.headers as Record<string, string> || {}),
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401 && onUnauthorizedCallback) {
      onUnauthorizedCallback();
    }
    const error = await response.json().catch(() => ({ detail: 'API Request Failed' }));
    const detail = error.detail;
    const message = typeof detail === 'string'
      ? detail
      : (Array.isArray(detail)
        ? detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ')
        : JSON.stringify(detail) || `Error ${response.status}: ${response.statusText}`);
    throw new Error(message);
  }

  if (response.status === 204) return {} as T;
  return response.json();
}

export const api = {
  get: <T>(endpoint: string) => request<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, data?: any) => request<T>(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: <T>(endpoint: string, data?: any) => request<T>(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: <T>(endpoint: string) => request<T>(endpoint, { method: 'DELETE' }),
  setToken: (newToken: string | null) => { token = newToken; },
  setOnUnauthorized: (callback: () => void) => { onUnauthorizedCallback = callback; },
};
