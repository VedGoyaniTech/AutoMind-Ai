import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Car, Mail, Lock, User as UserIcon, ShieldCheck, Check, AlertCircle, Eye, EyeOff, CheckCircle2, Sparkles } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';
import { User } from '../types/user';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { registerAccount, login, isAuthenticated } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleInstantDemo = () => {
    setIsLoading(true);
    setError('');
    const instantDemoUser: User = {
      id: (Date.now() % 10000) + 100,
      full_name: fullName.trim() || 'Alex Vance',
      email: email.trim() || 'demo@automind.ai',
      is_admin: true,
      preference: {
        id: 1,
        answer_detail: 'Balanced',
        units: 'Metric',
        currency: 'INR'
      },
      created_at: new Date().toISOString()
    };
    login('demo-instant-access-token', instantDemoUser);
    navigate('/app');
  };

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/app', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const getPasswordStrength = (pwd: string) => {
    if (!pwd) return { score: 0, text: '', color: 'bg-slate-700' };
    if (pwd.length < 8) return { score: 1, text: 'Weak (min 8 chars)', color: 'bg-rose-500' };
    if (pwd.length < 12) return { score: 2, text: 'Good', color: 'bg-amber-500' };
    return { score: 3, text: 'Strong', color: 'bg-emerald-500' };
  };

  const strength = getPasswordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!fullName.trim()) {
      setError('Please enter your full name.');
      return;
    }

    if (!email.trim() || !email.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsLoading(true);

    try {
      const res = await registerAccount({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        confirm_password: confirmPassword,
      });

      setSuccessMessage(res.message || 'Account created successfully! Redirecting...');

      setTimeout(() => {
        navigate('/app');
      }, 600);
    } catch (err: any) {
      console.error('Registration error:', err);
      if (err.code === 'ERR_NETWORK' || !err.response) {
        setError('Cannot connect to backend server. Please verify the backend is running, or continue directly with Instant Demo Session.');
      } else {
        const detail = err.response?.data?.detail;
        if (typeof detail === 'string') {
          setError(detail);
        } else if (Array.isArray(detail) && detail.length > 0) {
          setError(detail[0].msg || 'Validation failed. Please check your inputs.');
        } else if (typeof detail === 'object' && detail?.msg) {
          setError(detail.msg);
        } else if (err.response?.data?.message) {
          setError(err.response.data.message);
        } else {
          setError('Failed to create account. Please try again.');
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row selection:bg-[#722F37]/20" style={{ background: '#E8DCC6', color: '#1A1614' }}>
      {/* Left Split */}
      <div
        className="md:w-1/2 p-8 lg:p-12 flex flex-col justify-between relative overflow-hidden"
        style={{ background: '#DFD2BA', borderRight: '1px solid #B7A89A' }}
      >
        <Link to="/" className="flex items-center gap-2.5 z-10">
          <div className="p-2 rounded-xl text-white shadow-sm" style={{ background: '#722F37' }}>
            <Car className="w-5 h-5" />
          </div>
          <span className="text-xl font-bold" style={{ color: '#1A1614' }}>AutoMind AI</span>
        </Link>

        <div className="my-12 z-10 max-w-md">
          <h2 className="text-3xl font-extrabold leading-tight" style={{ color: '#1A1614' }}>
            Join the future of intelligent car research.
          </h2>
          <p className="text-sm mt-3 leading-relaxed" style={{ color: '#5C524A' }}>
            Create your account to unlock full automotive vector search, side-by-side spec comparison matrix, and top 5 verified website sources.
          </p>

          <div className="mt-8 space-y-3">
            {[
              'Hybrid RAG Search across 1M+ car specs',
              'Grounded answer generation with verified sources',
              'Side-by-side multi-car comparison matrix',
            ].map((item, idx) => (
              <div key={idx} className="flex items-center gap-2.5 text-xs" style={{ color: '#1A1614' }}>
                <div className="p-1 rounded-full bg-emerald-500/20 text-emerald-700">
                  <Check className="w-3.5 h-3.5" />
                </div>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="text-xs flex items-center gap-2 z-10" style={{ color: '#5C524A' }}>
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Zero Spam & Password Hashed with Bcrypt</span>
        </div>
      </div>

      {/* Right Split: Register Card */}
      <div className="md:w-1/2 p-8 lg:p-16 flex items-center justify-center" style={{ background: '#E8DCC6' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md space-y-6"
        >
          <div>
            <h2 className="text-2xl font-bold" style={{ color: '#1A1614' }}>Create Account</h2>
            <p className="text-sm mt-1" style={{ color: '#5C524A' }}>Get instant access to AutoMind AI</p>
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="p-3.5 rounded-xl text-xs font-medium space-y-2.5"
                style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', color: '#991B1B' }}
              >
                <div className="flex items-center gap-2 font-bold" style={{ color: '#DC2626' }}>
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>Registration Notice</span>
                </div>
                <p>{error}</p>
                {error.includes('Cannot connect') && (
                  <button
                    type="button"
                    onClick={handleInstantDemo}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white shadow-sm transition-opacity hover:opacity-90 mt-1"
                    style={{ background: '#722F37' }}
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    Continue with Instant Demo Access
                  </button>
                )}
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
              label="Full Name"
              type="text"
              placeholder="Alex Vance"
              icon={UserIcon}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />

            <Input
              label="Email Address"
              type="email"
              placeholder="alex@example.com"
              icon={Mail}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <div className="space-y-1 relative">
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
                style={{ color: '#857A70' }}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>

              {password && (
                <div className="flex items-center gap-2 pt-1">
                  <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: '#DFD2BA' }}>
                    <div
                      className={`h-full ${strength.color} transition-all duration-300`}
                      style={{ width: `${(strength.score / 3) * 100}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-semibold" style={{ color: '#5C524A' }}>{strength.text}</span>
                </div>
              )}
            </div>

            <Input
              label="Confirm Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              icon={Lock}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full mt-2"
              isLoading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#B7A89A]/40" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="px-2 font-medium" style={{ background: '#E8DCC6', color: '#857A70' }}>Or</span>
            </div>
          </div>

          {/* Instant Demo Access Button */}
          <Button
            type="button"
            variant="outline"
            size="lg"
            className="w-full border-[#B7A89A] hover:bg-[#DFD2BA] transition-all flex items-center justify-center gap-2"
            style={{ color: '#1A1614' }}
            onClick={handleInstantDemo}
            disabled={isLoading}
          >
            <Sparkles className="w-4 h-4 text-amber-600" />
            Continue with Instant Demo
          </Button>

          <div className="text-center text-xs" style={{ color: '#5C524A' }}>
            Already have an account?{' '}
            <Link to="/login" className="font-semibold hover:underline" style={{ color: '#722F37' }}>
              Sign In
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
