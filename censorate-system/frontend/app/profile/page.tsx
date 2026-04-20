'use client';

import { useState } from 'react';
import { User, Mail, Calendar, Save, Edit } from 'lucide-react';
import { useAuth } from '@/app/hooks/useAuth';

export default function ProfilePage() {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');

  const userAlias = user?.name || (user?.email ? user.email.split('@')[0] : 'User');

  const handleSave = () => {
    // TODO: Implement profile update
    setIsEditing(false);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-lg border border-gray-200/60 p-8">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Profile</h1>
            <p className="text-sm text-gray-500 mt-1">Manage your account settings</p>
          </div>
          <button
            onClick={() => isEditing ? handleSave() : setIsEditing(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors text-sm font-medium"
          >
            {isEditing ? (
              <>
                <Save size={16} />
                Save
              </>
            ) : (
              <>
                <Edit size={16} />
                Edit
              </>
            )}
          </button>
        </div>

        {/* Avatar Section */}
        <div className="flex items-center gap-6 mb-8 pb-8 border-b border-gray-100">
          <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white text-3xl font-bold shadow-lg">
            {userAlias.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{userAlias}</h2>
            <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
              <Mail size={14} />
              {user?.email}
            </p>
          </div>
        </div>

        {/* Profile Form */}
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Display Name
            </label>
            {isEditing ? (
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50/80 border border-gray-200/80 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none transition-all"
                placeholder="Enter your name"
              />
            ) : (
              <div className="px-4 py-3 bg-gray-50/50 border border-gray-200/50 rounded-xl text-gray-700">
                {name || userAlias}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Email
            </label>
            <div className="px-4 py-3 bg-gray-50/50 border border-gray-200/50 rounded-xl text-gray-500">
              {user?.email}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Member Since
            </label>
            <div className="px-4 py-3 bg-gray-50/50 border border-gray-200/50 rounded-xl text-gray-500 flex items-center gap-2">
              <Calendar size={16} />
              {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
