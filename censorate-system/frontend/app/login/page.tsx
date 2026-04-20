'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Eye, EyeOff, ArrowRight, Loader2, Kanban } from 'lucide-react';
import { useAuth } from '@/app/hooks/useAuth';
import { clsx } from 'clsx';

type AuthMode = 'standard' | 'ldap';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, isAuthenticated, clearError } = useAuth();

  const [mode, setMode] = useState<AuthMode>('standard');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // Clear errors when switching modes
  useEffect(() => {
    setLocalError(null);
    clearError();
  }, [mode, clearError]);

  // Clear error when typing
  useEffect(() => {
    if (localError || error) {
      setLocalError(null);
      clearError();
    }
  }, [email, password, localError, error, clearError]);

  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!email.trim()) {
      setLocalError('Email is required');
      emailRef.current?.focus();
      return;
    }

    if (!password) {
      setLocalError('Password is required');
      passwordRef.current?.focus();
      return;
    }

    const result = await login(email, password);
    if (result) {
      router.push('/');
    }
  };

  const displayError = localError || error;

  return (
    <div className="min-h-screen bg-gray-50/50 flex flex-col font-sans">
      <main className="flex-grow flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md flex flex-col gap-10">
          {/* Logo & Brand */}
          <div className="flex flex-col items-center text-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Kanban className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
              Censorate
            </h1>
            <p className="text-sm text-gray-500 font-medium">
              AI-native requirement management
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-white/80 backdrop-blur-xl rounded-3xl p-8 flex flex-col gap-8 shadow-lg border border-gray-200/60">
            {/* Auth Switcher */}
            <div className="flex p-1 bg-gray-100/70 rounded-2xl">
              <button
                type="button"
                onClick={() => setMode('standard')}
                className={clsx(
                  'flex-1 py-2 text-sm font-semibold rounded-xl transition-colors',
                  mode === 'standard'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                )}
              >
                Standard Sign In
              </button>
              <button
                type="button"
                onClick={() => setMode('ldap')}
                className={clsx(
                  'flex-1 py-2 text-sm font-semibold rounded-xl transition-colors',
                  mode === 'ldap'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                )}
              >
                LDAP / Enterprise
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="flex flex-col gap-6">
              {/* Email/Username Input */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold tracking-wider uppercase text-gray-500 ml-1">
                  {mode === 'ldap' ? 'Username' : 'Email or Username'}
                </label>
                <input
                  ref={emailRef}
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={mode === 'ldap' ? 'your.username' : 'name@company.com'}
                  className={clsx(
                    'w-full h-12 px-4 bg-gray-100/70 border-none rounded-2xl transition-all placeholder:text-gray-400 outline-none',
                    'focus:ring-2 focus:ring-blue-500/30 focus:bg-white',
                    displayError && 'ring-2 ring-red-500/50'
                  )}
                />
              </div>

              {/* Password Input */}
              <div className="flex flex-col gap-1.5">
                <div className="flex justify-between items-center ml-1">
                  <label className="text-xs font-bold tracking-wider uppercase text-gray-500">
                    Password
                  </label>
                  <a
                    href="#"
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700"
                  >
                    Forgot Password?
                  </a>
                </div>
                <div className="relative">
                  <input
                    ref={passwordRef}
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className={clsx(
                      'w-full h-12 px-4 pr-12 bg-gray-100/70 border-none rounded-2xl transition-all placeholder:text-gray-400 outline-none',
                      'focus:ring-2 focus:ring-blue-500/30 focus:bg-white',
                      displayError && 'ring-2 ring-red-500/50'
                    )}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Error Message */}
              {displayError && (
                <div className="text-sm text-red-600 text-center" role="alert">
                  {displayError}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-white font-semibold rounded-2xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/25"
                style={{
                  background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)'
                }}
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative flex items-center justify-center">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200/60" />
              </div>
              <span className="relative px-4 bg-white/0 text-xs font-medium text-gray-400 tracking-widest uppercase">
                New to Censorate?
              </span>
            </div>

            {/* Request Account Button */}
            <button
              type="button"
              className="w-full h-12 bg-gray-100/70 text-gray-700 font-semibold rounded-2xl hover:bg-gray-200/70 transition-colors"
            >
              Request an Account
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full bg-gray-50/50">
        <div className="w-full flex flex-col md:flex-row justify-between items-center px-8 py-12 max-w-7xl mx-auto">
          <div className="flex flex-col gap-2 items-center md:items-start mb-8 md:mb-0">
            <span className="text-lg font-bold tracking-tight text-gray-900">
              Censorate
            </span>
            <p className="text-xs text-gray-400">
              © 2024 Censorate. All rights reserved.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-x-8 gap-y-4">
            <a
              href="#"
              className="text-xs font-medium tracking-wider uppercase text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              Privacy Policy
            </a>
            <a
              href="#"
              className="text-xs font-medium tracking-wider uppercase text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              Terms of Service
            </a>
            <a
              href="#"
              className="text-xs font-medium tracking-wider uppercase text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              Security
            </a>
            <a
              href="#"
              className="text-xs font-medium tracking-wider uppercase text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              Help Center
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
