'use client';

import { Bell, User, Clock, X } from 'lucide-react';
import { Notification } from '@/app/stores/notificationStore';

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: string) => void;
  onRemove: (id: string) => void;
  onClick: (notification: Notification) => void;
}

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'reassignment':
      return <User size={18} className="text-blue-500" />;
    case 'due_date_reminder':
      return <Clock size={18} className="text-orange-500" />;
    case 'mention':
      return <Bell size={18} className="text-purple-500" />;
    default:
      return <Bell size={18} className="text-gray-500" />;
  }
};

const getTimeAgo = (date: Date) => {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
};

export default function NotificationItem({
  notification,
  onMarkAsRead,
  onRemove,
  onClick
}: NotificationItemProps) {
  return (
    <div
      className={`group relative p-4 transition-all duration-200 cursor-pointer border-b border-gray-100 last:border-b-0 hover:bg-gray-50/80 ${
        !notification.read ? 'bg-blue-50/50' : ''
      }`}
      onClick={() => {
        if (!notification.read) {
          onMarkAsRead(notification.id);
        }
        onClick(notification);
      }}
    >
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
          !notification.read ? 'bg-blue-100' : 'bg-gray-100'
        }`}>
          {getNotificationIcon(notification.type)}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <h4 className={`text-sm font-semibold leading-tight ${
                !notification.read ? 'text-gray-900' : 'text-gray-700'
              }`}>
                {notification.title}
              </h4>
              <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                {notification.message}
              </p>
            </div>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove(notification.id);
              }}
              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded-lg transition-all"
            >
              <X size={14} className="text-gray-400" />
            </button>
          </div>

          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-400">
              {getTimeAgo(notification.createdAt)}
            </span>
            {!notification.read && (
              <span className="w-2 h-2 rounded-full bg-blue-500" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
