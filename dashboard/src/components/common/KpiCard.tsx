import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badgeText?: string;
  badgeType?: 'default' | 'danger' | 'warning' | 'success' | 'info';
  onClick?: () => void;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badgeText,
  badgeType = 'default',
  onClick,
}) => {
  const badgeClasses = {
    default: 'bg-slate-800 text-slate-300 border-slate-700',
    danger: 'bg-rose-950 text-rose-300 border-rose-700 font-bold animate-pulse',
    warning: 'bg-amber-950/90 text-amber-300 border-amber-700/80 font-semibold',
    success: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80 font-medium',
    info: 'bg-sky-950/80 text-sky-300 border-sky-800/80 font-medium',
  };

  // Distinct visual tier styling
  let containerTierClass = 'bg-slate-900/95 border-slate-800/90 hover:border-slate-700';
  let iconContainerClass = 'bg-slate-800/80 text-slate-300 border-slate-700/50';

  if (badgeType === 'danger' && Number(value) > 0) {
    containerTierClass = 'bg-gradient-to-b from-rose-950/40 to-slate-900/95 border-rose-700/80 tactical-border-rose';
    iconContainerClass = 'bg-rose-900/40 text-rose-400 border-rose-700/60';
  } else if (badgeType === 'warning' && (typeof value === 'number' ? value > 0 : value !== 'N/A')) {
    containerTierClass = 'bg-gradient-to-b from-amber-950/25 to-slate-900/95 border-amber-700/60 tactical-border-amber';
    iconContainerClass = 'bg-amber-900/40 text-amber-400 border-amber-700/50';
  } else if (badgeType === 'info') {
    containerTierClass = 'bg-gradient-to-b from-sky-950/20 to-slate-900/95 border-slate-800/90 hover:border-sky-800/60';
    iconContainerClass = 'bg-sky-900/30 text-sky-400 border-sky-800/50';
  }

  const cardClass = `rounded-xl p-4 shadow-xl border backdrop-blur-md transition-all duration-200 ${containerTierClass} ${
    onClick ? 'cursor-pointer hover:translate-y-[-1px]' : ''
  }`;

  return (
    <div onClick={onClick} className={cardClass}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 font-mono">
          {title}
        </span>
        <div className={`p-2 rounded-lg border ${iconContainerClass}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="flex items-baseline justify-between mt-1">
        <span className="text-2xl lg:text-3xl font-extrabold tracking-tight text-white font-mono">
          {value}
        </span>
        {badgeText && (
          <span className={`text-[10px] px-2 py-0.5 rounded border uppercase font-mono tracking-tight ${badgeClasses[badgeType]}`}>
            {badgeText}
          </span>
        )}
      </div>
      {subtitle && (
        <div className="mt-1.5 text-xs text-slate-400 truncate font-sans">
          {subtitle}
        </div>
      )}
    </div>
  );
};

