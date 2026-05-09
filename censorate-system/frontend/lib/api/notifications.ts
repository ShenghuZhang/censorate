// frontend/lib/api/notifications.ts
import { api } from './client';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  read: boolean;
  createdAt: string;
  requirementId?: string;
  link?: string;
}

export const notificationsAPI = {
  getNotifications: (limit = 50, offset = 0, unreadOnly = false) =>
    api.get<Notification[]>(`/notifications?limit=${limit}&offset=${offset}&unread_only=${unreadOnly}`),
  getUnreadCount: () =>
    api.get<number>('/notifications/unread-count'),
  markAsRead: (id: string) =>
    api.post<any>(`/notifications/${id}/read`),
  markAllAsRead: () =>
    api.post<any>('/notifications/read-all'),
  deleteNotification: (id: string) =>
    api.delete(`/notifications/${id}`),
};
