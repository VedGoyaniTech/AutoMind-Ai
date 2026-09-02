import React from 'react';
import { Sidebar } from './Sidebar';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen w-screen overflow-hidden" style={{ background: '#F7F4ED', color: '#0D0D0D' }}>
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto relative" style={{ background: '#F7F4ED' }}>
        {children}
      </main>
    </div>
  );
};
