import React from 'react';
import { PriorityBand } from '../types';
import { AlertCircle, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';

interface Props {
  score: number;
  band: PriorityBand;
  size?: 'sm' | 'md' | 'lg';
  showScore?: boolean;
}

export const PriorityBadge: React.FC<Props> = ({ score, band, size = 'md', showScore = true }) => {
  const styles = {
    LOW: {
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      icon: CheckCircle,
      label: 'Low Priority',
    },
    MEDIUM: {
      bg: 'bg-amber-50 text-amber-700 border-amber-200',
      icon: AlertTriangle,
      label: 'Medium Priority',
    },
    HIGH: {
      bg: 'bg-orange-50 text-orange-700 border-orange-200',
      icon: AlertCircle,
      label: 'High Priority',
    },
    CRITICAL: {
      bg: 'bg-red-50 text-red-700 border-red-200 font-semibold animate-pulse',
      icon: ShieldAlert,
      label: 'Critical Hazard',
    },
  }[band] || {
    bg: 'bg-slate-50 text-slate-700 border-slate-200',
    icon: AlertCircle,
    label: band,
  };

  const Icon = styles.icon;
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : size === 'lg' ? 'text-sm px-3 py-1.5' : 'text-xs px-2.5 py-1';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${styles.bg} ${sizeClass}`}
      role="status"
      aria-label={`${styles.label}, score ${score} out of 100`}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} aria-hidden="true" />
      <span>{styles.label}</span>
      {showScore && <span className="font-mono opacity-80">({Math.round(score)})</span>}
    </span>
  );
};
