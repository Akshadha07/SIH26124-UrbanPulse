import React from 'react';

interface PriorityBadgeProps {
  score: number;
  size?: 'sm' | 'md';
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ score, size = 'md' }) => {
  let color = 'bg-emerald-950/70 text-emerald-300 border-emerald-800';
  let label = 'LOW';

  if (score >= 80) {
    color = 'bg-rose-950/90 text-rose-200 border-rose-700 font-bold';
    label = 'CRITICAL';
  } else if (score >= 60) {
    color = 'bg-orange-950/80 text-orange-300 border-orange-700';
    label = 'HIGH';
  } else if (score >= 40) {
    color = 'bg-amber-950/80 text-amber-300 border-amber-800';
    label = 'MEDIUM';
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={'inline-flex items-center gap-1.5 rounded-full border ' + sizeClasses + ' ' + color}>
      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
      <span>{score.toFixed(1)}</span>
      <span className="opacity-75 font-mono text-[10px]">({label})</span>
    </span>
  );
};
