import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface ThinkingBubbleProps {
  stage: string;
  message: string;
  hasStartedStreaming: boolean;
}

const STAGE_LABELS: Record<string, string> = {
  understanding: 'Understanding query',
  searching: 'Searching database',
  vector_search: 'Running vector search',
  reranking: 'Reranking results',
  generating: 'Generating analysis',
  complete: 'Done',
};

export const ThinkingBubble: React.FC<ThinkingBubbleProps> = ({
  stage,
  message,
  hasStartedStreaming,
}) => {
  const [expanded, setExpanded] = useState(false);
  const stageLabel = STAGE_LABELS[stage] || stage;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.2 }}
      className="flex gap-3 max-w-2xl"
    >
      {/* Avatar */}
      <div
        style={{ background: '#F0ECE5', border: '1px solid #E2DDD6', minWidth: 32, height: 32 }}
        className="rounded-xl flex items-center justify-center shrink-0"
      >
        <svg width="15" height="15" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="#C96A2B" strokeWidth="1.5" />
          <circle cx="10" cy="10" r="3" fill="#C96A2B" opacity="0.7" />
        </svg>
      </div>

      {/* Bubble */}
      <div
        style={{
          background: '#FFFFFF',
          border: '1px solid #E2DDD6',
          borderRadius: 12,
          padding: '10px 14px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
          minWidth: 160,
        }}
      >
        {/* Header row — always visible */}
        <button
          onClick={() => setExpanded((p) => !p)}
          className="flex items-center gap-2 w-full text-left"
          style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}
        >
          {/* Thinking dots */}
          {!hasStartedStreaming && (
            <div className="flex items-center gap-1 mr-1">
              <span className="thinking-dot" />
              <span className="thinking-dot" />
              <span className="thinking-dot" />
            </div>
          )}

          <span
            className={hasStartedStreaming ? '' : 'shimmer-text'}
            style={{
              fontSize: '0.8rem',
              fontWeight: 500,
              color: hasStartedStreaming ? '#6B6560' : undefined,
              letterSpacing: '0.01em',
            }}
          >
            {hasStartedStreaming ? 'Researched' : stageLabel}
          </span>

          {/* Expand toggle */}
          <span style={{ marginLeft: 'auto', color: '#9C9590' }}>
            {expanded
              ? <ChevronDown size={13} />
              : <ChevronRight size={13} />
            }
          </span>
        </button>

        {/* Expandable detail */}
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              style={{ overflow: 'hidden' }}
            >
              <div
                style={{
                  marginTop: 8,
                  paddingTop: 8,
                  borderTop: '1px solid #E2DDD6',
                  fontSize: '0.75rem',
                  color: '#9C9590',
                  lineHeight: 1.5,
                }}
              >
                {[
                  { key: 'understanding', label: 'Parse query & extract constraints' },
                  { key: 'searching', label: 'Filter MySQL automotive database' },
                  { key: 'vector_search', label: 'Run semantic embedding search' },
                  { key: 'reranking', label: 'Merge & rerank via RRF algorithm' },
                  { key: 'generating', label: 'Synthesize structured AI analysis' },
                ].map(({ key, label }) => {
                  const stages = Object.keys(STAGE_LABELS);
                  const currentIdx = stages.indexOf(stage);
                  const itemIdx = stages.indexOf(key);
                  const isDone = itemIdx < currentIdx;
                  const isActive = key === stage;

                  return (
                    <div key={key} className="flex items-center gap-2 py-0.5">
                      <span style={{ width: 14, textAlign: 'center' }}>
                        {isDone
                          ? <span style={{ color: '#22C55E', fontSize: 10 }}>✓</span>
                          : isActive
                          ? <span style={{ color: '#C96A2B', fontSize: 10 }}>›</span>
                          : <span style={{ color: '#E2DDD6', fontSize: 10 }}>○</span>
                        }
                      </span>
                      <span style={{ color: isActive ? '#0D0D0D' : isDone ? '#9C9590' : '#C8C2BA' }}>
                        {label}
                      </span>
                    </div>
                  );
                })}

                {message && (
                  <div
                    style={{
                      marginTop: 6,
                      padding: '5px 8px',
                      background: '#F7F4ED',
                      borderRadius: 6,
                      fontSize: '0.7rem',
                      color: '#6B6560',
                      fontFamily: 'monospace',
                    }}
                  >
                    {message}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};
