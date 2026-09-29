import React, { useState, useEffect } from 'react';
import { Bell, MapPin, Radio, ShieldCheck, UserCheck, AlertTriangle } from 'lucide-react';

interface TopBarProps {
  notificationsCount?: number;
  wsConnected?: boolean;
  onClearNotifications?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  notificationsCount = 0,
  wsConnected = true,
}) => {
  const [currentTime, setCurrentTime] = useState<string>(new Date().toLocaleTimeString('en-IN', { hour12: false }));
  const [currentDate, setCurrentDate] = useState<string>(new Date().toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }));

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('en-IN', { hour12: false }));
      setCurrentDate(now.toLocaleDateString('en-IN', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-14 border-b border-slate-800/90 bg-[#070b13]/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30 select-none">
      {/* City & Municipal Node Identity */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-200">
          <MapPin className="w-3.5 h-3.5 text-rose-500" />
          <span>Vadodara Metropolitan Area</span>
        </div>
        <span className="text-slate-700">|</span>
        <div className="flex items-center gap-1.5 text-xs text-sky-400 font-mono">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>VMC Municipal Operations Control</span>
        </div>

        {/* Operational Threat Status Pill */}
        <div className="hidden md:flex items-center ml-2">
          {notificationsCount > 0 ? (
            <span className="inline-flex items-center gap-1.5 text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-rose-950/80 border border-rose-600 text-rose-300 animate-pulse">
              <AlertTriangle className="w-3 h-3 text-rose-400" />
              <span>DISASTER FAST-PATH ACTIVE ({notificationsCount})</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-emerald-950/40 border border-emerald-800/60 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <span>NOMINAL CITY OPERATIONS</span>
            </span>
          )}
        </div>
      </div>

      {/* Telemetry Chrono & Officer Identity */}
      <div className="flex items-center gap-5">
        {/* Stream Status Indicator */}
        <div className="hidden lg:flex items-center gap-1.5 font-mono text-[11px] px-2.5 py-1 rounded-md bg-slate-900/80 border border-slate-800">
          <Radio className={`w-3 h-3 ${wsConnected ? 'text-emerald-400 animate-pulse' : 'text-rose-500'}`} />
          <span className="text-slate-400">STREAM:</span>
          <span className={wsConnected ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
            {wsConnected ? 'ONLINE' : 'DISCONNECTED'}
          </span>
        </div>

        {/* Dynamic IST Atomic Clock */}
        <div className="text-right">
          <div className="text-xs font-mono font-extrabold text-white tracking-widest">
            {currentTime} <span className="text-[10px] font-normal text-slate-400">IST</span>
          </div>
          <div className="text-[10px] text-slate-400 font-mono">
            {currentDate}
          </div>
        </div>

        {/* Notification Bell */}
        <div className="relative">
          <button
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-colors relative"
            aria-label="Critical notifications"
          >
            <Bell className="w-4 h-4" />
            {notificationsCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-600 text-[10px] font-bold text-white flex items-center justify-center animate-pulse">
                {notificationsCount}
              </span>
            )}
          </button>
        </div>

        {/* Official Officer Identity */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-blue-950 border border-blue-700/60 flex items-center justify-center text-blue-300">
            <UserCheck className="w-4 h-4" />
          </div>
          <div className="hidden sm:block">
            <div className="text-xs font-semibold text-slate-200">
              Duty Officer
            </div>
            <div className="text-[10px] text-slate-400 font-mono">
              VMC Room #4
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

