'use client';

import { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50/50 flex flex-col overflow-hidden">
      {/* Header - sticky at top */}
      <Header onMenuClick={toggleSidebar} />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

        {/* Page content - scrollable */}
        <main className="flex-1 overflow-hidden">
          <div className="h-full overflow-y-auto overflow-x-hidden">
            <div className="p-6 md:p-8 lg:p-10">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
