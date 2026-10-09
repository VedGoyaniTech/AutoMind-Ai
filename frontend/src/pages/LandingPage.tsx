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
    <div className="min-h-screen selection:bg-[#722F37]/20 overflow-x-hidden" style={{ background: '#E8DCC6', color: '#1A1614' }}>
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex flex-col items-center text-center">
        {/* Glowing Background Blobs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-[#722F37]/10 blur-[120px] rounded-full -z-10 pointer-events-none" />

        {/* Top Tagline Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#DFD2BA] border border-[#B7A89A] text-[#722F37] text-xs font-semibold mb-6 shadow-sm"
        >
          <Sparkles className="w-4 h-4 text-[#722F37]" />
          <span>Next-Generation Automotive RAG Intelligence</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-[#1A1614] leading-tight max-w-4xl"
        >
          Understand Any Car.{' '}
          <span className="bg-gradient-to-r from-[#722F37] via-[#8E3E47] to-[#58242A] bg-clip-text text-transparent">
            Instantly.
          </span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-6 text-base sm:text-xl text-[#5C524A] max-w-2xl font-normal leading-relaxed"
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
          <p className="text-xs font-semibold text-[#5C524A] uppercase tracking-wider mb-3">Try Asking AutoMind:</p>
          <div className="flex flex-wrap items-center justify-center gap-2">
            {SAMPLE_QUESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => navigate(`/app?q=${encodeURIComponent(q)}`)}
                className="px-3.5 py-2 rounded-xl bg-[#FAF7F2] border border-[#B7A89A] hover:border-[#722F37] hover:bg-[#DFD2BA] text-xs text-[#1A1614] transition-all cursor-pointer shadow-sm text-left"
              >
                "{q}"
              </button>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Feature Grid */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-[#B7A89A]">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-[#1A1614]">Built for Automotive Research</h2>
          <p className="text-[#5C524A] mt-2 text-sm">Combines structured database precision with conversational AI explanations.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 rounded-2xl bg-[#FAF7F2] border border-[#B7A89A] hover:border-[#722F37] transition-all shadow-sm">
            <div className="p-3 rounded-xl bg-[#DFD2BA] text-[#722F37] w-fit mb-4">
              <Database className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-[#1A1614]">Hybrid RAG Retrieval</h3>
            <p className="text-sm text-[#5C524A] mt-2 leading-relaxed">
              Combines structured MySQL candidate filtering with sentence-transformers vector embeddings for high precision answers.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#FAF7F2] border border-[#B7A89A] hover:border-[#722F37] transition-all shadow-sm">
            <div className="p-3 rounded-xl bg-[#DFD2BA] text-[#722F37] w-fit mb-4">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-[#1A1614]">Top 5 Verified Sources</h3>
            <p className="text-sm text-[#5C524A] mt-2 leading-relaxed">
              Returns up to 5 real, non-fabricated website links with reliability scores so you can verify prices and brochure details.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#FAF7F2] border border-[#B7A89A] hover:border-[#722F37] transition-all shadow-sm">
            <div className="p-3 rounded-xl bg-[#DFD2BA] text-[#722F37] w-fit mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-[#1A1614]">AI Research Progress</h3>
            <p className="text-sm text-[#5C524A] mt-2 leading-relaxed">
              Watch real-time animated processing stages (understanding, searching, comparing, ranking) before token stream generation.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-[#B7A89A] text-center text-xs text-[#5C524A]">
        <p>© 2026 AutoMind AI — Intelligent Automotive Research Platform. Grounded in verified car data.</p>
      </footer>
    </div>
  );
};
