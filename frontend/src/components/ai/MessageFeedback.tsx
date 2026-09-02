import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Check, X, MessageSquare, AlertCircle } from 'lucide-react';
import { submitMessageFeedback } from '../../api/chat';

interface MessageFeedbackProps {
  conversationId: number;
  messageId: number;
  prompt?: string;
  responseContent?: string;
  initialRating?: 'up' | 'down';
}

const REASON_OPTIONS = [
  { code: 'incorrect_price', label: 'Incorrect price, RTO tax, or specs' },
  { code: 'not_relevant', label: 'Not relevant to my question' },
  { code: 'incomplete_answer', label: 'Incomplete or missing details' },
  { code: 'language_issue', label: 'Language / Translation issue' },
  { code: 'unsafe_inappropriate', label: 'Unsafe or inaccurate advice' },
  { code: 'other', label: 'Other' }
];

export const MessageFeedback: React.FC<MessageFeedbackProps> = ({
  conversationId,
  messageId,
  prompt,
  responseContent,
  initialRating
}) => {
  const [rating, setRating] = useState<'up' | 'down' | null>(initialRating || null);
  const [showReasonModal, setShowReasonModal] = useState(false);
  const [selectedReason, setSelectedReason] = useState<string>('incorrect_price');
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(!!initialRating);
  const [error, setError] = useState<string | null>(null);

  const handleRating = async (newRating: 'up' | 'down') => {
    if (isSubmitting) return;

    if (newRating === 'down') {
      setRating('down');
      setShowReasonModal(true);
      return;
    }

    // Direct submission for Thumbs Up
    setRating('up');
    setIsSubmitting(true);
    setError(null);

    try {
      await submitMessageFeedback({
        conversationId,
        messageId,
        rating: 'up',
        prompt,
        responseContent,
        locale: localStorage.getItem('automind_voice_lang') || 'en-IN'
      });
      setSubmitted(true);
    } catch (err: any) {
      console.error('Failed to submit thumbs up:', err);
      setRating(null);
      setError('Failed to record feedback');
      setTimeout(() => setError(null), 3000);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownvoteSubmit = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await submitMessageFeedback({
        conversationId,
        messageId,
        rating: 'down',
        reasonCode: selectedReason as any,
        comment: comment.trim() || undefined,
        prompt,
        responseContent,
        locale: localStorage.getItem('automind_voice_lang') || 'en-IN'
      });
      setSubmitted(true);
      setShowReasonModal(false);
    } catch (err: any) {
      console.error('Failed to submit thumbs down feedback:', err);
      setError('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative inline-flex items-center gap-1 mt-2 text-xs text-zinc-400">
      {/* Thumbs Up Button */}
      <button
        type="button"
        onClick={() => handleRating('up')}
        disabled={isSubmitting}
        aria-label="Mark this answer helpful"
        title="Helpful response"
        className={`p-1.5 rounded-lg border transition flex items-center gap-1 ${
          rating === 'up'
            ? 'bg-emerald-950/80 border-emerald-600 text-emerald-400'
            : 'bg-zinc-800/40 border-zinc-700/50 hover:bg-zinc-800 hover:text-zinc-200'
        }`}
      >
        <ThumbsUp className="w-3.5 h-3.5" />
      </button>

      {/* Thumbs Down Button */}
      <button
        type="button"
        onClick={() => handleRating('down')}
        disabled={isSubmitting}
        aria-label="Mark this answer not helpful"
        title="Report issue or unhelpful response"
        className={`p-1.5 rounded-lg border transition flex items-center gap-1 ${
          rating === 'down'
            ? 'bg-rose-950/80 border-rose-600 text-rose-400'
            : 'bg-zinc-800/40 border-zinc-700/50 hover:bg-zinc-800 hover:text-zinc-200'
        }`}
      >
        <ThumbsDown className="w-3.5 h-3.5" />
      </button>

      {submitted && (
        <span className="text-[11px] text-zinc-400 ml-1 flex items-center gap-0.5">
          <Check className="w-3 h-3 text-emerald-400" /> Feedback recorded
        </span>
      )}

      {error && (
        <span className="text-[11px] text-rose-400 ml-1 flex items-center gap-0.5">
          <AlertCircle className="w-3 h-3" /> {error}
        </span>
      )}

      {/* Thumbs Down Reason Modal */}
      {showReasonModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-zinc-900 border border-zinc-700 rounded-2xl p-5 max-w-md w-full shadow-2xl text-zinc-100">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
              <h3 className="text-sm font-semibold flex items-center gap-1.5 text-zinc-100">
                <MessageSquare className="w-4 h-4 text-rose-400" />
                Help Improve AutoMind AI
              </h3>
              <button
                onClick={() => setShowReasonModal(false)}
                className="p-1 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-3.5 space-y-3">
              <label className="block text-xs font-medium text-zinc-300">
                What went wrong with this response?
              </label>

              <div className="space-y-1.5">
                {REASON_OPTIONS.map((opt) => (
                  <label
                    key={opt.code}
                    className={`flex items-center gap-2 p-2 rounded-xl border text-xs cursor-pointer transition ${
                      selectedReason === opt.code
                        ? 'bg-indigo-950/60 border-indigo-500 text-indigo-200 font-medium'
                        : 'bg-zinc-800/40 border-zinc-700/50 text-zinc-300 hover:bg-zinc-800'
                    }`}
                  >
                    <input
                      type="radio"
                      name="feedback_reason"
                      value={opt.code}
                      checked={selectedReason === opt.code}
                      onChange={() => setSelectedReason(opt.code)}
                      className="accent-indigo-500"
                    />
                    <span>{opt.label}</span>
                  </label>
                ))}
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">
                  Optional notes or correct details:
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value.slice(0, 500))}
                  placeholder="e.g. Creta IVT on-road price in Mumbai should include 12% RTO..."
                  rows={3}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-xl p-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-hidden focus:ring-1 focus:ring-indigo-500"
                />
                <div className="text-[10px] text-zinc-500 text-right mt-0.5">
                  {comment.length} / 500
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 mt-4 pt-3 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => setShowReasonModal(false)}
                className="px-3 py-1.5 rounded-xl text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDownvoteSubmit}
                disabled={isSubmitting}
                className="px-4 py-1.5 rounded-xl text-xs bg-rose-600 hover:bg-rose-500 text-white font-medium shadow-md transition disabled:opacity-50"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
