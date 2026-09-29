import React from 'react';
import { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  description,
  actionText,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center rounded-xl border border-dashed border-slate-800 bg-slate-900/40">
      <div className="p-3 rounded-full bg-slate-800/80 text-slate-400 mb-3">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
      {description && (
        <p className="mt-1 text-xs text-slate-400 max-w-sm">{description}</p>
      )}
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-3 py-1.5 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
