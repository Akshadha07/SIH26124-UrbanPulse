import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl border border-rose-900/50 bg-rose-950/30 text-rose-200">
      <div className="flex items-center gap-3">
        <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
        <span className="text-xs">{message}</span>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-rose-200 bg-rose-900/50 hover:bg-rose-900 rounded-lg transition-colors border border-rose-800"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
};
