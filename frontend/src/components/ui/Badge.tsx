import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'info' | 'purple' | 'slate';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'primary',
  size = 'md',
}) => {
  const variantStyles = {
    primary: 'bg-[#722F37]/15 text-[#722F37] border-[#722F37]/30',
    success: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-700 border-amber-500/30',
    info: 'bg-cyan-500/15 text-cyan-700 border-cyan-500/30',
    purple: 'bg-[#DFD2BA] text-[#722F37] border-[#B7A89A]',
    slate: 'bg-[#DFD2BA] text-[#1A1614] border-[#B7A89A]',
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
  };

  return (
    <span className={`inline-flex items-center font-medium rounded-md border ${variantStyles[variant]} ${sizeStyles[size]}`}>
      {children}
    </span>
  );
};
