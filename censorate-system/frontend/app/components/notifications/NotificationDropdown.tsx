'use client';

import { useRouter } from 'next/navigation';
import { Bell, Check, Trash2 } from 'lucide-react';
import { useNotificationStore, Notification } from '@/app/stores/notificationStore';
import NotificationItem from './NotificationItem';

interface NotificationDropdownProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function NotificationDropdown({ isOpen, onClose }: NotificationDropdownProps) {
  const router = useRouter();
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll
  } = useNotificationStore();

  if (!isOpen) return null;

  const handleNotificationClick = (notification: Notification) => {
    if (notification.requirementId) {
      // Navigate to kanban board with requirement highlighted
      router.push('/kanban');
    }
    onClose();
  };

  return (
    <>
      <div className="fixed inset-0 z-40" onClick={onClose} />

      <div className="absolute top-full right-0 mt-2 w-96 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/80 z-50 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
            {unreadCount > 0 && (
              <span className="px-2 py-0.5 bg-blue-500 text-white text-xs font-bold rounded-full">
                {unreadCount}
              </span>
            )}
          </div>

          <div className="flex items-center gap-1">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded-xl transition-colors"
              >
                <Check size={14} />
                Mark all read
              </button>
            )}
            {notifications.length > 0 && (
              <button
                onClick={clearAll}
                className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-500 hover:bg-gray-100 rounded-xl transition-colors"
              >
                <Trash2 size={14} />
                Clear all
              </button>
            )}
          </div>
        </div>

        {/* Notification List */}
        <div className="max-h-96 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="p-8 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Bell size={32} className="text-gray-300" />
              </div>
              <h4 className="text-sm font-semibold text-gray-900 mb-1">No notifications</h4>
              <p className="text-xs text-gray-400">You&apos;re all caught up!</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onMarkAsRead={markAsRead}
                onRemove={removeNotification}
                onClick={handleNotificationClick}
              />
            ))
          )}
        </div>
      </div>
    </>
  );
}
