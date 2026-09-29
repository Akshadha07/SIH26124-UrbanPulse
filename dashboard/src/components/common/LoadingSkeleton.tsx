import React from 'react';

interface LoadingSkeletonProps {
  rows?: number;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ rows = 4, className = '' }) => {
  return (
    <div className={'space-y-3 animate-pulse ' + className}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-10 bg-slate-800/60 rounded-lg w-full"></div>
      ))}
    </div>
  );
};
