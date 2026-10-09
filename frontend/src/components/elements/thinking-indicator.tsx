import React, { useEffect, useState } from 'react';

export function ThinkingIndicator({
  label,
  className,
}: {
  label: string;
  className?: string;
}) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div
      className={`flex items-center gap-2.5 text-sm ${className || ''}`}
      style={{ color: '#5C524A' }}
    >
      <span
        aria-hidden
        className="size-2 shrink-0 animate-pulse rounded-full"
        style={{ background: '#722F37' }}
      />
      <span
        key={label}
        className="fade-in slide-in-from-bottom-1 animate-in relative inline-block leading-none duration-300 font-medium"
        style={{ color: '#1A1614' }}
      >
        <span>{label}</span>
      </span>
      <span className="tabular-nums text-xs font-mono" style={{ color: '#857A70' }}>
        {elapsedSeconds}s
      </span>
    </div>
  );
}
