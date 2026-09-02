import React from 'react';
import { ShieldCheck, Globe } from 'lucide-react';
import { SourceCard as SourceCardType } from '../../types/chat';

interface SourceCardProps {
  source: SourceCardType;
}

export const SourceCardComponent: React.FC<SourceCardProps> = ({ source }) => {
  return (
    <div
      className="p-3.5 rounded-xl transition-all duration-200 shadow-sm"
      style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
    >
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5">
          <div className="p-1 rounded" style={{ background: '#F7F4ED', color: '#C96A2B' }}>
            <Globe className="w-3.5 h-3.5" />
          </div>
          <span className="text-xs font-semibold" style={{ color: '#0D0D0D' }}>
            {source.website}
          </span>
        </div>

        <div className="flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded" style={{ background: '#ECFDF5', color: '#059669', border: '1px solid #A7F3D0' }}>
          <ShieldCheck className="w-3 h-3" />
          <span>{Math.round(source.reliability_score * 100)}% verified</span>
        </div>
      </div>

      <h5 className="text-xs font-bold line-clamp-1 mb-1" style={{ color: '#0D0D0D' }}>
        {source.title}
      </h5>

      <p className="text-[11px] line-clamp-2 leading-relaxed" style={{ color: '#6B6560' }}>
        {source.reason}
      </p>

      <div className="mt-2 text-[10px] font-mono tracking-tight truncate" style={{ color: '#9C9590' }}>
        {source.domain}
      </div>
    </div>
  );
};
