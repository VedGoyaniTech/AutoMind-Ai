import React from 'react';
import { ArrowUpIcon, Car } from "lucide-react";

export interface EmptyStateProps {
  greeting: string;
  suggestions: readonly string[];
  onSelectSuggestion: (suggestion: string) => void;
  className?: string;
}

export function EmptyState({
  greeting,
  suggestions,
  onSelectSuggestion,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={`flex w-full max-w-lg flex-col items-center gap-6 mx-auto py-12 ${className || ''}`}
    >
      <div className="p-3.5 rounded-2xl shadow-sm" style={{ background: '#DFD2BA', border: '1px solid #B7A89A', color: '#722F37' }}>
        <Car className="w-7 h-7" />
      </div>

      <h2 className="fade-in slide-in-from-bottom-1 animate-in fill-mode-both text-center text-2xl font-bold tracking-tight duration-500" style={{ color: '#1A1614' }}>
        {greeting}
      </h2>

      <div className="flex flex-wrap justify-center gap-2 max-w-md">
        {suggestions.map((suggestion, i) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => onSelectSuggestion(suggestion)}
            className="fade-in slide-in-from-bottom-2 animate-in fill-mode-both rounded-full px-4 py-2 text-xs font-medium transition-all duration-300 outline-none hover:-translate-y-px active:scale-[0.96] shadow-sm cursor-pointer hover:bg-[#DFD2BA]"
            style={{
              animationDelay: `${120 + i * 70}ms`,
              background: '#FAF7F2',
              border: '1px solid #B7A89A',
              color: '#1A1614'
            }}
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
