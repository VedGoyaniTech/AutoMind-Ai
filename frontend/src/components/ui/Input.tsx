import React from 'react';
import { LucideIcon } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: LucideIcon;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  icon: Icon,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label className="block text-xs font-semibold uppercase tracking-wider" style={{ color: '#5C524A' }}>
          {label}
        </label>
      )}
      <div className="relative rounded-xl shadow-sm">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none" style={{ color: '#857A70' }}>
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          className={`w-full rounded-xl ${
            Icon ? 'pl-10' : 'pl-4'
          } pr-4 py-2.5 text-sm outline-none transition-all duration-200 focus:border-[#722F37] ${className}`}
          style={{
            background: '#FAF7F2',
            border: error ? '1px solid #EF4444' : '1px solid #B7A89A',
            color: '#1A1614',
          }}
          {...props}
        />
      </div>
      {error && <p className="text-xs font-medium" style={{ color: '#EF4444' }}>{error}</p>}
    </div>
  );
};
