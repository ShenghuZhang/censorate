'use client';

import { usePathname, useRouter } from 'next/navigation';
import {
  Kanban,
  BarChart3,
  Settings as SettingsIcon,
  Brain,
  Bot,
} from 'lucide-react';
import { clsx } from 'clsx';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();

  const navigationGroups: {
    items: NavItem[];
    showDivider?: boolean;
  }[] = [
    {
      items: [
        { name: 'Kanban', href: '/kanban', icon: Kanban },
        { name: 'Analytics', href: '/analytics', icon: BarChart3 },
      ],
    },
    {
      items: [
        { name: 'Skills', href: '/skills', icon: Brain },
        { name: 'Agents', href: '/agents', icon: Bot },
        { name: 'Settings', href: '/settings', icon: SettingsIcon },
      ],
      showDivider: true,
    },
  ];

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  const handleNavigation = (href: string) => {
    router.push(href);
    onClose?.();
  };

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm lg:hidden z-40"
          onClick={onClose}
        />
      )}

      <aside className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-64 bg-white border-r border-gray-200
        transform transition-transform duration-300 ease-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        <div className="flex flex-col h-full">
          <div className="px-6 py-6 border-b border-gray-100/80">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <Kanban className="text-white" size={22} />
              </div>
              <span className="text-xl font-bold text-gray-900 tracking-tight">Censorate</span>
            </div>
          </div>

          <nav className="flex-1 px-3 py-5">
            {navigationGroups.map((group, groupIndex) => (
              <div key={groupIndex} className={clsx(groupIndex > 0 && 'mt-2')}>
                {group.showDivider && (
                  <div className="my-4 mx-2 border-t border-dashed border-gray-200" />
                )}
                <div className="space-y-1">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);

                    return (
                      <button
                        key={item.name}
                        onClick={() => handleNavigation(item.href)}
                        className={clsx(
                          'w-full flex items-center gap-3 px-4 py-3 rounded-2xl',
                          'text-sm font-medium transition-all duration-200',
                          active
                            ? 'bg-blue-50/80 text-blue-700 shadow-sm'
                            : 'text-gray-600 hover:bg-gray-50/80 hover:text-gray-900'
                        )}
                      >
                        <Icon
                          size={20}
                          className={active ? 'text-blue-600' : 'text-gray-400'}
                        />
                        <span>{item.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>
        </div>
      </aside>
    </>
  );
}
