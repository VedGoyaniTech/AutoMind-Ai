import React, { useState } from 'react';
import { Settings, User as UserIcon, Sliders, CheckCircle2 } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';
import { updatePreferences } from '../api/auth';

export const SettingsPage: React.FC = () => {
  const { user, refreshUser } = useAuth();

  const [answerDetail, setAnswerDetail] = useState(user?.preference?.answer_detail || 'Balanced');
  const [units, setUnits] = useState(user?.preference?.units || 'Metric');
  const [currency, setCurrency] = useState(user?.preference?.currency || 'INR');
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);

    try {
      await updatePreferences({ answer_detail: answerDetail, units, currency });
      await refreshUser();
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-6 lg:p-10 max-w-4xl mx-auto w-full space-y-8">
        <div className="border-b border-[#B7A89A] pb-6">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1A1614] flex items-center gap-2.5">
            <Settings className="w-7 h-7 text-[#722F37]" />
            Account & AI Preferences
          </h1>
          <p className="text-xs sm:text-sm text-[#5C524A] mt-1">
            Customize response detail level, display units, and default currency for AutoMind research answers.
          </p>
        </div>

        {savedSuccess && (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 text-xs font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            Preferences updated successfully!
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* User Profile Info */}
          <div className="p-6 rounded-3xl bg-[#FAF7F2] border border-[#B7A89A] space-y-4 shadow-sm">
            <h3 className="text-sm font-bold text-[#1A1614] uppercase tracking-wider flex items-center gap-2">
              <UserIcon className="w-4 h-4 text-[#722F37]" />
              User Profile
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-[#5C524A]">Full Name:</span>
                <p className="font-bold text-[#1A1614] text-sm mt-0.5">{user?.full_name}</p>
              </div>
              <div>
                <span className="text-[#5C524A]">Email Address:</span>
                <p className="font-bold text-[#1A1614] text-sm mt-0.5">{user?.email}</p>
              </div>
            </div>
          </div>

          {/* AI Answer Preferences */}
          <div className="p-6 rounded-3xl bg-[#FAF7F2] border border-[#B7A89A] space-y-6 shadow-sm">
            <h3 className="text-sm font-bold text-[#1A1614] uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-[#722F37]" />
              AI Answer Configuration
            </h3>

            {/* Answer Detail */}
            <div>
              <label className="block text-xs font-bold text-[#5C524A] uppercase tracking-wider mb-2">
                Answer Detail Level
              </label>
              <div className="grid grid-cols-3 gap-3">
                {['Concise', 'Balanced', 'Detailed'].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setAnswerDetail(option as any)}
                    className={`p-3 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                      answerDetail === option
                        ? 'bg-[#722F37] border-[#722F37] text-white shadow-sm'
                        : 'bg-[#DFD2BA] border-[#B7A89A] text-[#1A1614] hover:border-[#722F37]'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            {/* Units & Currency */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-bold text-[#5C524A] uppercase tracking-wider mb-2">
                  Display Units
                </label>
                <select
                  value={units}
                  onChange={(e) => setUnits(e.target.value as 'Metric' | 'Imperial')}
                  className="w-full bg-[#FAF7F2] border border-[#B7A89A] rounded-xl px-3 py-2.5 text-xs text-[#1A1614] focus:outline-none focus:border-[#722F37]"
                >
                  <option value="Metric">Metric (km/l, km, mm, bhp)</option>
                  <option value="Imperial">Imperial (mpg, miles, inches, hp)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5C524A] uppercase tracking-wider mb-2">
                  Default Currency
                </label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full bg-[#FAF7F2] border border-[#B7A89A] rounded-xl px-3 py-2.5 text-xs text-[#1A1614] focus:outline-none focus:border-[#722F37]"
                >
                  <option value="INR">INR (₹ Indian Rupee / Lakh)</option>
                  <option value="USD">USD ($ US Dollar)</option>
                  <option value="EUR">EUR (€ Euro)</option>
                </select>
              </div>
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={saving}
          >
            Save AI Preferences
          </Button>
        </form>
      </div>
    </AppLayout>
  );
};
