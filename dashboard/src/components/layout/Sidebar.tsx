import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Bus, 
  AlertTriangle, 
  Flame, 
  Activity, 
  ClipboardList, 
  ShieldAlert,
  Radio,
  Building2
} from 'lucide-react';

interface SidebarProps {
  wsConnected: boolean;
  activeIncidentsCount?: number;
  criticalAlertsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  wsConnected,
  activeIncidentsCount = 0,
  criticalAlertsCount = 0,
}) => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Live Fleet', path: '/fleet', icon: Bus },
    { 
      name: 'Incidents', 
      path: '/incidents', 
      icon: AlertTriangle,
      badge: activeIncidentsCount > 0 ? activeIncidentsCount : undefined,
      badgeColor: 'bg-amber-950 text-amber-300 border-amber-700/80 font-bold',
    },
    { 
      name: 'Emergency Center', 
      path: '/emergency', 
      icon: Flame,
      badge: criticalAlertsCount > 0 ? criticalAlertsCount : undefined,
      badgeColor: 'bg-rose-950 text-rose-300 border-rose-600 font-bold animate-pulse',
    },
    { name: 'Road Health', path: '/road-health', icon: Activity },
    { name: 'Work Orders', path: '/work-orders', icon: ClipboardList },
  ];

  return (
    <aside className="w-64 bg-[#070b13] border-r border-slate-800/90 flex flex-col justify-between shrink-0 h-screen sticky top-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-800/80 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-sky-700 flex items-center justify-center shadow-lg shadow-blue-950/60 border border-sky-400/30">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold tracking-tight text-white flex items-center gap-1.5 text-sm">
              <span>BEL UrbanPulse</span>
              <span className="text-[9px] bg-sky-500/20 text-sky-300 border border-sky-500/40 px-1 py-0.2 rounded font-mono font-bold">
                SIH26124
              </span>
            </div>
            <div className="text-[11px] text-slate-400">
              Vadodara Municipal Corp.
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="p-3">
          <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest px-3 mb-2.5">
            Operations Command
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                      isActive
                        ? 'bg-sky-950/50 text-sky-200 border-l-2 border-sky-400 border-r border-t border-b border-sky-900/40 shadow-md font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/70 border border-transparent'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge !== undefined && (
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${item.badgeColor}`}
                    >
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/60">
        <div className="space-y-2.5">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-400">
              <Radio className="w-3.5 h-3.5 text-cyan-400" />
              <span>WebSocket Stream</span>
            </div>
            <div className="flex items-center gap-1.5 font-mono text-[11px]">
              <span
                className={`w-2 h-2 rounded-full ${
                  wsConnected ? 'bg-emerald-400 shadow-emerald-500/50 shadow-sm animate-pulse' : 'bg-rose-500'
                }`}
              ></span>
              <span className={wsConnected ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                {wsConnected ? 'LIVE' : 'OFFLINE'}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-400">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              <span>Telemetry Feed</span>
            </div>
            <span className="font-mono text-[9px] font-bold text-amber-300 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/30">
              SIMULATED FLEET
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};

