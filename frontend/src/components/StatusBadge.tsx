import React from 'react';
import { IssueStatus } from '../types';

interface Props {
  status: IssueStatus | string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<Props> = ({ status, size = 'md' }) => {
  const configs: Record<string, { bg: string; dot: string; text: string }> = {
    REPORTED: { bg: 'bg-blue-50 text-blue-700 border-blue-200', dot: 'bg-blue-500', text: 'Reported' },
    VERIFIED: { bg: 'bg-purple-50 text-purple-700 border-purple-200', dot: 'bg-purple-500', text: 'Verified' },
    IN_PROGRESS: { bg: 'bg-amber-50 text-amber-700 border-amber-200', dot: 'bg-amber-500', text: 'In Progress' },
    RESOLVED: { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', dot: 'bg-emerald-500', text: 'Resolved' },
    REJECTED: { bg: 'bg-slate-100 text-slate-600 border-slate-200', dot: 'bg-slate-400', text: 'Rejected' },
  };

  const c = configs[status] || { bg: 'bg-slate-50 text-slate-700 border-slate-200', dot: 'bg-slate-400', text: status };
  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border ${c.bg} ${sizeClasses} font-medium`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} aria-hidden="true" />
      {c.text}
    </span>
  );
};
