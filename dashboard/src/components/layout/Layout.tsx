import React from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

interface LayoutProps {
  children: React.ReactNode;
  wsConnected: boolean;
  activeIncidentsCount?: number;
  criticalAlertsCount?: number;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  wsConnected,
  activeIncidentsCount = 0,
  criticalAlertsCount = 0,
}) => {
  return (
    <div className="flex min-h-screen bg-[#070b13] text-slate-100 antialiased">
      <Sidebar
        wsConnected={wsConnected}
        activeIncidentsCount={activeIncidentsCount}
        criticalAlertsCount={criticalAlertsCount}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar notificationsCount={criticalAlertsCount} wsConnected={wsConnected} />
        <main className="flex-1 p-5 md:p-6 overflow-y-auto max-w-[1920px] w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );

};
