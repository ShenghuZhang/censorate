import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type NotificationType = 'reassignment' | 'due_date_reminder' | 'mention';

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

  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  toggleDropdown: () => void;
  setIsOpen: (open: boolean) => void;
  clearAll: () => void;
}

// Demo notifications
const demoNotifications: Notification[] = [
  {
    id: '1',
    type: 'reassignment',
    title: 'Requirement Assigned',
    message: 'REQ-2: Dashboard design has been assigned to you',
    read: false,
    createdAt: new Date(Date.now() - 30 * 60 * 1000),
    requirementId: 'req-2'
  },
  {
    id: '2',
    type: 'due_date_reminder',
    title: 'Due Tomorrow',
    message: 'REQ-1: User login system is due tomorrow',
    read: false,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    requirementId: 'req-1'
  },
  {
    id: '3',
    type: 'mention',
    title: 'You were mentioned',
    message: '@you in comment on REQ-3: API endpoints',
    read: true,
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
    requirementId: 'req-3'
  }
];

export const useNotificationStore = create<NotificationState>()(
  devtools(
    (set, get) => ({
      notifications: demoNotifications,
      unreadCount: demoNotifications.filter(n => !n.read).length,
      isOpen: false,

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
      },

      markAsRead: (id: string) => {
        set((state) => ({
          notifications: state.notifications.map(n =>
            n.id === id ? { ...n, read: true } : n
          ),
          unreadCount: state.notifications.find(n => n.id === id && !n.read)
            ? state.unreadCount - 1
            : state.unreadCount
        }));
      },

      markAllAsRead: () => {
        set((state) => ({
          notifications: state.notifications.map(n => ({ ...n, read: true })),
          unreadCount: 0
        }));
      },

      removeNotification: (id: string) => {
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id),
          unreadCount: state.notifications.find(n => n.id === id && !n.read)
            ? state.unreadCount - 1
            : state.unreadCount
        }));
      },

      toggleDropdown: () => {
        set((state) => ({ isOpen: !state.isOpen }));
      },

      setIsOpen: (open: boolean) => {
        set({ isOpen: open });
      },

      clearAll: () => {
        set({ notifications: [], unreadCount: 0 });
      }
    })
  )
);
