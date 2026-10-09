import React from 'react';
import { Sidebar } from './Sidebar';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen w-screen overflow-hidden" style={{ background: '#E8DCC6', color: '#1A1614' }}>
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto relative" style={{ background: '#E8DCC6' }}>
        {children}
      </main>
    </div>
  );
};
