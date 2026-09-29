import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const s = status.toUpperCase();

  let colorClasses = 'bg-slate-800 text-slate-300 border-slate-700';

  if (s === 'REPORTED' || s === 'DETECTED') {
    colorClasses = 'bg-sky-950/70 text-sky-300 border-sky-800/80';
  } else if (s === 'CONFIRMED' || s === 'ASSIGNED') {
    colorClasses = 'bg-indigo-950/70 text-indigo-300 border-indigo-800/80';
  } else if (s === 'IN_PROGRESS' || s === 'IN_REPAIR') {
    colorClasses = 'bg-amber-950/70 text-amber-300 border-amber-800/80';
  } else if (s === 'RESOLVED' || s === 'VERIFIED' || s === 'VERIFIED_CLOSED') {
    colorClasses = 'bg-emerald-950/70 text-emerald-300 border-emerald-800/80';
  } else if (s === 'ESCALATED_DISASTER' || s === 'CRITICAL') {
    colorClasses = 'bg-rose-950/90 text-rose-200 border-rose-700 animate-pulse font-bold';
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={'inline-flex items-center rounded-full border font-medium uppercase tracking-wider ' + sizeClasses + ' ' + colorClasses}>
      {status.replace(/_/g, ' ')}
    </span>
  );
};
