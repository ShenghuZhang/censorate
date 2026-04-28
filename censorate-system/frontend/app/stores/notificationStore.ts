import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { notificationsAPI, Notification as APINotification } from '@/lib/api/notifications';

export type NotificationType = 'mention' | 'assignment' | 'due_date_reminder';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  createdAt: Date;
  requirementId?: string;
}

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchNotifications: (limit?: number, offset?: number, unreadOnly?: boolean) => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  removeNotification: (id: string) => Promise<void>;
  toggleDropdown: () => void;
  setIsOpen: (open: boolean) => void;
  clearAll: () => void;
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt' | 'read'>) => void;
}

// Convert API notification to store format
const convertAPIToStore = (apiNotif: APINotification): Notification => ({
  id: apiNotif.id,
  type: apiNotif.type,
  title: apiNotif.title,
  message: apiNotif.message,
  read: apiNotif.read,
  createdAt: new Date(apiNotif.createdAt),
  requirementId: apiNotif.requirementId
});

export const useNotificationStore = create<NotificationState>()(
  devtools(
    (set, get) => ({
      notifications: [],
      unreadCount: 0,
      isOpen: false,
      isLoading: false,
      error: null,

      fetchNotifications: async (limit = 50, offset = 0, unreadOnly = false) => {
        set({ isLoading: true, error: null });
        try {
          const apiNotifications = await notificationsAPI.getNotifications(limit, offset, unreadOnly);
          const notifications = apiNotifications.map(convertAPIToStore);
          set({
            notifications,
            unreadCount: notifications.filter(n => !n.read).length,
            isLoading: false
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch notifications',
            isLoading: false
          });
        }
      },

      fetchUnreadCount: async () => {
        try {
          const count = await notificationsAPI.getUnreadCount();
          set({ unreadCount: count });
        } catch (error) {
          console.error('Failed to fetch unread count:', error);
        }
      },

      markAsRead: async (id: string) => {
        try {
          await notificationsAPI.markAsRead(id);
          set((state) => ({
            notifications: state.notifications.map(n =>
              n.id === id ? { ...n, read: true } : n
            ),
            unreadCount: state.notifications.find(n => n.id === id && !n.read)
              ? state.unreadCount - 1
              : state.unreadCount
          }));
        } catch (error) {
          console.error('Failed to mark notification as read:', error);
        }
      },

      markAllAsRead: async () => {
        try {
          await notificationsAPI.markAllAsRead();
          set((state) => ({
            notifications: state.notifications.map(n => ({ ...n, read: true })),
            unreadCount: 0
          }));
        } catch (error) {
          console.error('Failed to mark all notifications as read:', error);
        }
      },

      removeNotification: async (id: string) => {
        try {
          await notificationsAPI.deleteNotification(id);
          set((state) => ({
            notifications: state.notifications.filter(n => n.id !== id),
            unreadCount: state.notifications.find(n => n.id === id && !n.read)
              ? state.unreadCount - 1
              : state.unreadCount
          }));
        } catch (error) {
          console.error('Failed to delete notification:', error);
        }
      },

      toggleDropdown: () => {
        set((state) => ({ isOpen: !state.isOpen }));
      },

      setIsOpen: (open: boolean) => {
        set({ isOpen: open });
      },

      clearAll: () => {
        set({ notifications: [], unreadCount: 0 });
      },

      addNotification: (notification) => {
        const newNotification: Notification = {
          ...notification,
          id: 'notif-' + Date.now(),
          createdAt: new Date(),
          read: false
        };

        set((state) => ({
          notifications: [newNotification, ...state.notifications],
          unreadCount: state.unreadCount + 1
        }));
      }
    })
  )
);
