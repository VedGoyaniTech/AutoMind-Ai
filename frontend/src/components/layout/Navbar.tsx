import React from 'react';
import { Link } from 'react-router-dom';
import { Car, Sparkles, UserCheck } from 'lucide-react';
import { Button } from '../ui/Button';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#E8DCC6]/90 backdrop-blur-md border-b border-[#B7A89A]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-[#722F37] shadow-sm text-white">
            <Car className="w-5 h-5" />
          </div>
          <span className="text-lg font-extrabold text-[#1A1614] tracking-tight flex items-center gap-1">
            AutoMind <span className="text-[#722F37] font-mono text-xs px-1.5 py-0.5 rounded bg-[#DFD2BA] border border-[#B7A89A]">AI</span>
          </span>
        </Link>

        {/* Center Links */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-[#5C524A]">
          <a href="#features" className="hover:text-[#722F37] transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-[#722F37] transition-colors">How It Works</a>
          <a href="#ai-research" className="hover:text-[#722F37] transition-colors">AI Architecture</a>
        </div>

        {/* Right CTA */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Link to="/app">
              <Button variant="primary" size="sm" icon={Sparkles}>
                Dashboard
              </Button>
            </Link>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link to="/register">
                <Button variant="primary" size="sm">
                  Get Started
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};
