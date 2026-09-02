import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, Send, Scale, Bookmark, MessageSquare, Compass, ArrowRight } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');

  const SUGGESTED_PROMPTS = [
    { title: 'Best SUVs under ₹20 Lakh', desc: 'Find top 5-star safety rated SUVs with 6 airbags.' },
    { title: 'Compare Creta vs Seltos', desc: 'Side-by-side spec, mileage, and feature comparison.' },
    { title: 'Best EV for City Driving', desc: 'Compare Tata Nexon EV vs Mahindra XUV400 EV.' },
    { title: 'Safest 7-Seater Family Cars', desc: 'Vehicle recommendations for a family of 5-7.' },
  ];

  const handleSend = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!prompt.trim()) return;
    navigate(`/app?q=${encodeURIComponent(prompt)}`);
  };

  return (
    <AppLayout>
      <div className="p-6 lg:p-10 max-w-6xl mx-auto w-full space-y-8">
        {/* Top Header Greeting */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6"
          style={{ borderBottom: '1px solid #E2DDD6' }}
        >
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: '#0D0D0D' }}>
              Welcome back, <span style={{ color: '#C96A2B' }}>{user?.full_name || 'Researcher'}</span>
            </h1>
            <p className="text-xs sm:text-sm mt-1" style={{ color: '#6B6560' }}>
              Ask anything about vehicle specifications, prices, mileage, safety, or request source recommendations.
            </p>
          </div>

          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold w-fit" style={{ background: '#EFECE5', border: '1px solid #E2DDD6', color: '#C96A2B' }}>
            <Sparkles className="w-4 h-4" />
            <span>Hybrid RAG Engine Online</span>
          </div>
        </motion.div>

        {/* Central Composer Input */}
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          onSubmit={handleSend}
          className="relative rounded-2xl p-3 shadow-sm"
          style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
        >
          <div className="relative flex items-center">
            <Sparkles className="w-5 h-5 absolute left-3.5" style={{ color: '#C96A2B' }} />
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ask anything about cars (e.g., Best SUVs under ₹20 lakh with 6 airbags)..."
              className="w-full bg-transparent pl-11 pr-24 py-3.5 text-sm sm:text-base outline-none"
              style={{ color: '#0D0D0D' }}
            />
            <Button
              type="submit"
              variant="primary"
              size="md"
              icon={Send}
              className="absolute right-2"
            >
              Ask
            </Button>
          </div>
        </motion.form>

        {/* Suggested Prompt Cards */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider mb-4 flex items-center gap-2" style={{ color: '#6B6560' }}>
            <Compass className="w-4 h-4" style={{ color: '#C96A2B' }} />
            Popular Research Prompts
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {SUGGESTED_PROMPTS.map((item, idx) => (
              <motion.div
                key={idx}
                whileHover={{ scale: 1.01 }}
                onClick={() => navigate(`/app?q=${encodeURIComponent(item.title)}`)}
                className="p-4 rounded-2xl transition-all cursor-pointer shadow-sm flex flex-col justify-between"
                style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
              >
                <div>
                  <h4 className="text-sm font-bold mb-1" style={{ color: '#0D0D0D' }}>{item.title}</h4>
                  <p className="text-xs leading-relaxed" style={{ color: '#6B6560' }}>{item.desc}</p>
                </div>
                <div className="mt-4 flex items-center gap-1 text-xs font-semibold group" style={{ color: '#C96A2B' }}>
                  <span>Start Research</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Quick Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4" style={{ borderTop: '1px solid #E2DDD6' }}>
          <div
            onClick={() => navigate('/saved')}
            className="p-5 rounded-2xl transition-all cursor-pointer flex items-center justify-between shadow-sm"
            style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
          >
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl" style={{ background: '#F7F4ED', color: '#C96A2B' }}>
                <Bookmark className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold" style={{ color: '#0D0D0D' }}>Saved Vehicles</h4>
                <p className="text-xs" style={{ color: '#6B6560' }}>View bookmarked cars</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4" style={{ color: '#9C9590' }} />
          </div>

          <div
            onClick={() => navigate('/compare')}
            className="p-5 rounded-2xl transition-all cursor-pointer flex items-center justify-between shadow-sm"
            style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
          >
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl" style={{ background: '#F7F4ED', color: '#C96A2B' }}>
                <Scale className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold" style={{ color: '#0D0D0D' }}>Compare Models</h4>
                <p className="text-xs" style={{ color: '#6B6560' }}>Side-by-side spec matrix</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4" style={{ color: '#9C9590' }} />
          </div>

          <div
            onClick={() => navigate('/app')}
            className="p-5 rounded-2xl transition-all cursor-pointer flex items-center justify-between shadow-sm"
            style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
          >
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl" style={{ background: '#F7F4ED', color: '#C96A2B' }}>
                <MessageSquare className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold" style={{ color: '#0D0D0D' }}>New AI Session</h4>
                <p className="text-xs" style={{ color: '#6B6560' }}>Start fresh research</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4" style={{ color: '#9C9590' }} />
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
