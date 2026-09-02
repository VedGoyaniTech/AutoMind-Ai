import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, ShieldCheck, Database, Cpu, Search, CheckCircle2, Zap, Car, Compass } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Button } from '../components/ui/Button';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const SAMPLE_QUESTIONS = [
    "What are the best SUVs under ₹20 lakh with 6 airbags?",
    "Compare Hyundai Creta vs Kia Seltos.",
    "Which electric car gives the highest range in India?",
    "Show 5-star safety rated family cars.",
  ];

  return (
    <div className="min-h-screen bg-background text-slate-100 selection:bg-indigo-500/30 overflow-x-hidden">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex flex-col items-center text-center">
        {/* Glowing Background Blobs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-600/20 to-purple-600/20 blur-[120px] rounded-full -z-10 pointer-events-none" />

        {/* Top Tagline Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900/80 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-6 shadow-lg shadow-indigo-500/10"
        >
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span>Next-Generation Automotive RAG Intelligence</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-tight max-w-4xl"
        >
          Understand Any Car.{' '}
          <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-cyan-400 bg-clip-text text-transparent">
            Instantly.
          </span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-6 text-base sm:text-xl text-slate-400 max-w-2xl font-normal leading-relaxed"
        >
          Search, compare, and research vehicles using an AI assistant powered by structured automotive data, hybrid vector search, and verified citations.
        </motion.p>

        {/* Hero CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 flex flex-col sm:flex-row items-center gap-4"
        >
          <Button
            variant="primary"
            size="lg"
            onClick={() => navigate('/app')}
            icon={Sparkles}
          >
            Ask AutoMind AI
          </Button>

          <a href="#features">
            <Button variant="outline" size="lg" icon={Compass}>
              Explore Features
            </Button>
          </a>
        </motion.div>

        {/* Interactive Sample Prompt Chips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-12 w-full max-w-3xl"
        >
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Try Asking AutoMind:</p>
          <div className="flex flex-wrap items-center justify-center gap-2">
            {SAMPLE_QUESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => navigate(`/app?q=${encodeURIComponent(q)}`)}
                className="px-3.5 py-2 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-800 text-xs text-slate-300 hover:text-white transition-all cursor-pointer shadow-sm text-left"
              >
                "{q}"
              </button>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Feature Grid */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-slate-800/60">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-white">Built for Automotive Research</h2>
          <p className="text-slate-400 mt-2 text-sm">Combines structured database precision with conversational AI explanations.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-xl">
            <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 w-fit mb-4">
              <Database className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Hybrid RAG Retrieval</h3>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              Combines structured MySQL candidate filtering with sentence-transformers vector embeddings for high precision answers.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-xl">
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 w-fit mb-4">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Top 5 Verified Sources</h3>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              Returns up to 5 real, non-fabricated website links with reliability scores so you can verify prices and brochure details.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-xl">
            <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 w-fit mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">AI Research Progress</h3>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              Watch real-time animated processing stages (understanding, searching, comparing, ranking) before token stream generation.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-900 text-center text-xs text-slate-500">
        <p>© 2026 AutoMind AI — Intelligent Automotive Research Platform. Grounded in verified car data.</p>
      </footer>
    </div>
  );
};
