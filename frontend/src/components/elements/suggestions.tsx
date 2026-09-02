import React from 'react';

export interface SuggestionsProps {
  suggestions: readonly string[];
  selectedSuggestion?: string | null;
  onSuggestion: (suggestion: string) => void;
  variant?: "pills" | "list";
  className?: string;
}

export function Suggestions({
  suggestions,
  selectedSuggestion,
  onSuggestion,
  variant = "pills",
  className,
}: SuggestionsProps) {
  const isList = variant === "list";

  return (
    <div
      className={
        isList
          ? `flex w-full max-w-sm flex-col gap-2 ${className || ''}`
          : `flex max-w-md flex-wrap justify-center gap-2 ${className || ''}`
      }
    >
      {suggestions.map((suggestion, index) => (
        <button
          key={suggestion}
          type="button"
          aria-pressed={selectedSuggestion === suggestion}
          onClick={() => onSuggestion(suggestion)}
          className={`fade-in slide-in-from-bottom-2 animate-in fill-mode-both flex cursor-pointer items-center text-xs font-medium transition-all duration-200 hover:-translate-y-px active:scale-[0.96] shadow-sm ${
            isList ? "w-full rounded-2xl px-4 py-2.5 text-start" : "rounded-full px-4 py-2"
          }`}
          style={{
            animationDelay: `${index * 70}ms`,
            background: selectedSuggestion === suggestion ? '#0D0D0D' : '#FFFFFF',
            color: selectedSuggestion === suggestion ? '#FFFFFF' : '#0D0D0D',
            border: '1px solid #E2DDD6'
          }}
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}
