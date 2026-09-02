import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Car, Mail, Lock, Sparkles, ShieldCheck, AlertCircle, Eye, EyeOff, CheckCircle2 } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { loginUser } from '../api/auth';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();

  const [email, setEmail] = useState('demo@automind.ai');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Redirect to app if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/app', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!email.trim() || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setIsLoading(true);

    try {
      const data = await loginUser({ email, password, remember_me: rememberMe });
      setSuccessMessage('Login successful! Redirecting to Dashboard...');
      
      login(data.access_token, data.user);
      
      setTimeout(() => {
        navigate('/app');
      }, 500);
    } catch (err: any) {
      console.error('Login error:', err);
      if (err.code === 'ERR_NETWORK' || !err.response) {
        setError('Cannot connect to backend server at http://localhost:8000. Please ensure the FastAPI backend is running.');
      } else {
        setError(err.response?.data?.detail || 'Incorrect email or password.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await loginUser({ email: 'demo@automind.ai', password: 'password123', remember_me: true });
      login(data.access_token, data.user);
      navigate('/app');
    } catch (err: any) {
      console.error('Demo login failed:', err);
      setError('Backend server is not reachable. Please start the FastAPI server at http://localhost:8000 and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row selection:bg-amber-500/20" style={{ background: '#F7F4ED', color: '#0D0D0D' }}>
      {/* Left Split: Animated AI / Automotive Visualization */}
      <div
        className="md:w-1/2 p-8 lg:p-12 flex flex-col justify-between relative overflow-hidden"
        style={{ background: '#EFECE5', borderRight: '1px solid #E2DDD6' }}
      >
        {/* Top Logo */}
        <Link to="/" className="flex items-center gap-2.5 z-10">
          <div className="p-2 rounded-xl text-white shadow-sm" style={{ background: '#C96A2B' }}>
            <Car className="w-5 h-5" />
          </div>
          <span className="text-xl font-bold" style={{ color: '#0D0D0D' }}>AutoMind AI</span>
        </Link>

        {/* Center Animated Visualizer */}
        <div className="my-12 z-10 max-w-md">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-6 rounded-2xl shadow-sm relative"
            style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg" style={{ background: '#F7F4ED', color: '#C96A2B' }}>
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold" style={{ color: '#0D0D0D' }}>Automotive Neural Engine</h4>
                <p className="text-xs" style={{ color: '#6B6560' }}>Indexing 1M+ car models & verified sources</p>
              </div>
            </div>

            <div className="space-y-2 text-xs font-mono p-3 rounded-xl" style={{ background: '#F7F4ED', border: '1px solid #E2DDD6', color: '#0D0D0D' }}>
              <p style={{ color: '#C96A2B' }}>&gt; Query: "SUV under ₹20 Lakh with 6 airbags"</p>
              <p className="text-emerald-700">&gt; Matched 14 candidate models via hybrid RAG</p>
              <p style={{ color: '#6B6560' }}>&gt; Citing 5 verified sources...</p>
            </div>
          </motion.div>

          <h2 className="mt-8 text-2xl font-bold leading-tight" style={{ color: '#0D0D0D' }}>
            Research cars with grounded AI intelligence.
          </h2>
          <p className="text-sm mt-2" style={{ color: '#6B6560' }}>
            Log in to access personalized recommendations, vehicle comparison matrices, and saved car lists.
          </p>
        </div>

        {/* Bottom Tagline */}
        <div className="text-xs flex items-center gap-2 z-10" style={{ color: '#6B6560' }}>
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>AES-256 Encrypted & Secure JWT Session</span>
        </div>
      </div>

      {/* Right Split: Login Card */}
      <div className="md:w-1/2 p-8 lg:p-16 flex items-center justify-center" style={{ background: '#F7F4ED' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md space-y-6"
        >
          <div>
            <h2 className="text-2xl font-bold" style={{ color: '#0D0D0D' }}>Welcome back</h2>
            <p className="text-sm mt-1" style={{ color: '#6B6560' }}>Sign in to continue your automotive research</p>
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="p-3.5 rounded-xl text-xs font-medium space-y-2"
                style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', color: '#991B1B' }}
              >
                <div className="flex items-center gap-2 font-bold" style={{ color: '#DC2626' }}>
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>Authentication Notice</span>
                </div>
                <p>{error}</p>
                <button
                  type="button"
                  onClick={handleDemoLogin}
                  className="text-xs underline font-semibold block pt-1 cursor-pointer"
                  style={{ color: '#C96A2B' }}
                >
                  Click here to enter with Instant Demo Mode
                </button>
              </motion.div>
            )}

            {successMessage && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3.5 rounded-xl text-xs font-medium flex items-center gap-2"
                style={{ background: '#ECFDF5', border: '1px solid #6EE7B7', color: '#065F46' }}
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>{successMessage}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              placeholder="demo@automind.ai"
              icon={Mail}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                icon={Lock}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-[34px] transition-colors"
                style={{ color: '#9C9590' }}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center gap-2 cursor-pointer select-none" style={{ color: '#6B6560' }}>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded"
                />
                <span>Remember me</span>
              </label>
              <a href="#" className="font-medium hover:underline" style={{ color: '#C96A2B' }}>Forgot password?</a>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-3 px-4 rounded-xl font-medium text-sm text-white transition-all shadow-sm disabled:opacity-50 cursor-pointer"
              style={{ background: '#C96A2B' }}
            >
              {isLoading ? 'Verifying Credentials...' : 'Sign In'}
            </button>
          </form>

          <div className="text-center text-xs" style={{ color: '#6B6560' }}>
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold hover:underline" style={{ color: '#C96A2B' }}>
              Create Account
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
