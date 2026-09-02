import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Database, Scale, CheckCircle2, Trophy, Loader2 } from 'lucide-react';
import { ResearchStage } from '../../types/chat';

interface ResearchProgressProps {
  currentStage: ResearchStage;
  currentMessage: string;
}

const STAGES = [
  { key: 'understanding', label: 'Understanding Question', icon: Sparkles },
  { key: 'searching', label: 'Searching Car Database', icon: Database },
  { key: 'comparing', label: 'Comparing Specifications', icon: Scale },
  { key: 'ranking', label: 'Ranking Top Sources', icon: Trophy },
  { key: 'generating', label: 'Generating Grounded Answer', icon: CheckCircle2 },
];

export const ResearchProgress: React.FC<ResearchProgressProps> = ({
  currentStage,
  currentMessage,
}) => {
  const getStageIndex = (stage: ResearchStage) => {
    const idx = STAGES.findIndex((s) => s.key === stage);
    return idx >= 0 ? idx : 0;
  };

  const activeIdx = getStageIndex(currentStage);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="p-5 rounded-2xl bg-slate-900/90 border border-indigo-500/30 shadow-xl shadow-indigo-950/20 backdrop-blur-xl relative overflow-hidden my-4"
    >
      {/* Background Animated Gradient Pulse */}
      <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-cyan-500/10 blur-xl animate-pulse-slow -z-10" />

      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center">
            <span className="animate-ping absolute inline-flex h-4 w-4 rounded-full bg-indigo-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              AI Research Progress
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">{currentMessage || 'Processing automotive context...'}</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-indigo-400 font-mono bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span>Stage {activeIdx + 1}/5</span>
        </div>
      </div>

      {/* Progress Steps Timeline */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
        {STAGES.map((s, idx) => {
          const isDone = idx < activeIdx;
          const isCurrent = idx === activeIdx;
          const Icon = s.icon;

          return (
            <motion.div
              key={s.key}
              initial={{ opacity: 0.7 }}
              animate={{ opacity: isCurrent || isDone ? 1 : 0.4 }}
              className={`p-2.5 rounded-xl border flex flex-col items-center text-center gap-1.5 transition-all duration-300 ${
                isCurrent
                  ? 'bg-indigo-600/15 border-indigo-500/50 shadow-md shadow-indigo-500/10'
                  : isDone
                  ? 'bg-slate-800/60 border-emerald-500/30'
                  : 'bg-slate-900/40 border-slate-800'
              }`}
            >
              <div
                className={`p-2 rounded-lg ${
                  isCurrent
                    ? 'bg-indigo-500 text-white'
                    : isDone
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-slate-800 text-slate-500'
                }`}
              >
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
              </div>
              <span className={`text-[11px] font-medium leading-tight ${isCurrent ? 'text-indigo-300 font-semibold' : isDone ? 'text-emerald-400' : 'text-slate-500'}`}>
                {s.label}
              </span>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};
