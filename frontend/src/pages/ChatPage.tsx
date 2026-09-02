import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion } from 'framer-motion';
import { 
  Send, Square, Copy, Check, Car, ArrowUpIcon, Sparkles
} from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { StreamingText } from '../components/elements/streaming-text';
import { ThinkingIndicator } from '../components/elements/thinking-indicator';
import { Suggestions } from '../components/elements/suggestions';
import { EmptyState } from '../components/elements/empty-state';
import { SourceCardComponent } from '../components/ai/SourceCard';
import { CarCardComponent } from '../components/ai/CarCard';
import { VehicleGalleryCard } from '../components/ai/VehicleGalleryCard';
import { PricingQuoteCard, PricingQuoteData } from '../components/pricing/PricingQuoteCard';
import { MessageFeedback } from '../components/ai/MessageFeedback';
import { VoiceInputButton } from '../components/chat/VoiceInputButton';
import { getConversationMessages } from '../api/chat';
import { ChatMessage, SourceCard, ResearchStage, VehicleGallery } from '../types/chat';
import { CarVariantSummary } from '../types/car';

const SUGGESTIONS_LIST = [
  "Best SUVs under ₹20 lakh with 6 airbags",
  "Compare Tata Nexon EV vs Mahindra XUV400",
  "Which 5 websites should I check before buying?",
  "Safest 7-seater family cars"
];

const STAGE_LABELS: Record<string, string> = {
  understanding: 'Analyzing automotive query constraints...',
  searching: 'Searching database & vector index...',
  comparing: 'Comparing specification candidates...',
  ranking: 'Ranking top verified sources...',
  generating: 'Generating grounded AI response...',
  complete: 'Done',
};

export const ChatPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const convIdParam = searchParams.get('conv');
  const queryParam = searchParams.get('q');

  const [conversationId, setConversationId] = useState<number | null>(
    convIdParam ? parseInt(convIdParam) : null
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputPrompt, setInputPrompt] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  // Active SSE streaming state
  const [currentStage, setCurrentStage] = useState<ResearchStage>('understanding');
  const [currentStageMessage, setCurrentStageMessage] = useState('');
  const [streamingText, setStreamingText] = useState('');
  const [activeSources, setActiveSources] = useState<SourceCard[]>([]);
  const [activeCars, setActiveCars] = useState<CarVariantSummary[]>([]);
  const [activeGallery, setActiveGallery] = useState<VehicleGallery | null>(null);
  const [activePricingQuote, setActivePricingQuote] = useState<PricingQuoteData | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isStreamingRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const loadedConvIdRef = useRef<number | null>(convIdParam ? parseInt(convIdParam) : null);
  const autoSentQueryRef = useRef<string | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingText, isStreaming]);

  // Load existing conversation if URL param changes and NOT already loaded
  useEffect(() => {
    if (isStreamingRef.current) return;

    const cid = convIdParam ? parseInt(convIdParam) : null;
    if (cid === loadedConvIdRef.current) return;

    loadedConvIdRef.current = cid;
    setConversationId(cid);

    if (cid) {
      loadMessages(cid);
    } else {
      setMessages([]);
    }
  }, [convIdParam]);

  // Auto-send query param if present from hero/prompt chips ONCE
  useEffect(() => {
    if (queryParam && queryParam !== autoSentQueryRef.current && !isStreamingRef.current) {
      autoSentQueryRef.current = queryParam;
      setInputPrompt(queryParam);
      sendChat(queryParam);
    }
  }, [queryParam]);

  const historyAbortControllerRef = useRef<AbortController | null>(null);

  const loadMessages = async (cid: number) => {
    if (historyAbortControllerRef.current) {
      historyAbortControllerRef.current.abort();
    }
    const ctrl = new AbortController();
    historyAbortControllerRef.current = ctrl;

    try {
      const msgs = await getConversationMessages(cid);
      if (!ctrl.signal.aborted) {
        setMessages(msgs);
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        console.error('Failed to load conversation messages:', e);
      }
    }
  };

  const sendChat = async (promptText: string) => {
    if (!promptText.trim() || isStreamingRef.current) return;

    const userMsg: ChatMessage = { role: 'user', content: promptText };
    setMessages((prev) => [...prev, userMsg]);
    setInputPrompt('');

    isStreamingRef.current = true;
    setIsStreaming(true);
    setStreamingText('');
    setActiveSources([]);
    setActiveCars([]);
    const cleanLower = promptText.trim().toLowerCase().replace(/[!?.]$/, '');
    const isGreeting = ['hi', 'hii', 'hiii', 'hello', 'hey', 'heyy', 'thanks', 'thank you', 'ok', 'okay', 'good morning', 'good evening', 'good night', 'bye', 'goodbye'].includes(cleanLower);

    setCurrentStage(isGreeting ? 'generating' : 'understanding');
    setCurrentStageMessage(isGreeting ? '' : 'Analyzing automotive query constraints...');

    const abortCtrl = new AbortController();
    abortControllerRef.current = abortCtrl;

    const token = localStorage.getItem('automind_token');
    if (!token) {
      isStreamingRef.current = false;
      setIsStreaming(false);
      navigate('/login', { replace: true });
      return;
    }

    try {
      const payloadBody = JSON.stringify({
        conversation_id: loadedConvIdRef.current,
        message: promptText,
      });

      const headersDict = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      };

      let response: Response;
      try {
        response = await fetch('/api/v1/chat/stream', {
          method: 'POST',
          headers: headersDict,
          body: payloadBody,
          signal: abortCtrl.signal,
        });
        if (!response.ok && response.status !== 401) {
          throw new Error(`Proxy status ${response.status}`);
        }
      } catch (proxyErr: any) {
        if (proxyErr.name === 'AbortError') throw proxyErr;
        response = await fetch('http://localhost:8000/api/v1/chat/stream', {
          method: 'POST',
          headers: headersDict,
          body: payloadBody,
          signal: abortCtrl.signal,
        });
      }

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('automind_token');
          localStorage.removeItem('automind_user');
          navigate('/login', { replace: true });
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let activeConvId = loadedConvIdRef.current;
      let finalStreamText = '';
      let finalSources: SourceCard[] = [];
      let finalCars: CarVariantSummary[] = [];
      let finalGallery: VehicleGallery | null = null;
      let finalPricingQuote: PricingQuoteData | null = null;
      let finalMessageId: number | undefined = undefined;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const rawLine of lines) {
            const line = rawLine.trim();
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));

                if (data.conversation_id && !activeConvId) {
                  activeConvId = data.conversation_id;
                  loadedConvIdRef.current = data.conversation_id;
                  setConversationId(data.conversation_id);
                  setSearchParams({ conv: String(data.conversation_id) }, { replace: true });
                }

                if (data.event_type === 'progress') {
                  setCurrentStage(data.stage);
                  setCurrentStageMessage(data.message);
                } else if (data.event_type === 'token') {
                  finalStreamText += data.token;
                  setStreamingText(finalStreamText);
                } else if (data.event_type === 'gallery') {
                  finalGallery = data;
                  setActiveGallery(data);
                } else if (data.event_type === 'pricing_quote') {
                  finalPricingQuote = data;
                  setActivePricingQuote(data);
                } else if (data.event_type === 'sources') {
                  finalSources = data.sources || [];
                  setActiveSources(finalSources);
                } else if (data.event_type === 'cars') {
                  finalCars = data.cars || [];
                  setActiveCars(finalCars);
                } else if (data.event_type === 'error') {
                  console.error('[ChatSSE Error Event]', data.message);
                  setStreamingText('');
                  finalStreamText = '';
                } else if (data.event_type === 'complete') {
                  finalMessageId = data.message_id;
                  const contentToSave = finalStreamText.trim() || data.content;
                  if (contentToSave && !contentToSave.startsWith('⚠️')) {
                    const assistantMsg: ChatMessage = {
                      id: finalMessageId,
                      conversation_id: activeConvId || undefined,
                      role: 'assistant',
                      content: contentToSave,
                      metadata: {
                        sources: finalSources,
                        cars: finalCars,
                        gallery: finalGallery || undefined,
                        pricing_quote: finalPricingQuote || undefined,
                      },
                    };
                    setMessages((prev) => [...prev, assistantMsg]);
                  }
                  setStreamingText('');
                  setActiveGallery(null);
                  setActivePricingQuote(null);
                  finalStreamText = '';
                }
              } catch (err) {
                console.error('Error parsing SSE chunk:', err);
              }
            }
          }
        }
      }

      // Safety fallback: If stream ended without complete event, only save clean valid text
      if (finalStreamText.trim() && !finalStreamText.startsWith('⚠️')) {
        const assistantMsg: ChatMessage = {
          id: finalMessageId,
          conversation_id: activeConvId || undefined,
          role: 'assistant',
          content: finalStreamText.trim(),
          metadata: {
            sources: finalSources,
            cars: finalCars,
            gallery: finalGallery || undefined,
          },
        };
        setMessages((prev) => [...prev, assistantMsg]);
        setStreamingText('');
        setActiveGallery(null);
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Chat SSE Error:', err);
      }
      setStreamingText('');
    } finally {
      isStreamingRef.current = false;
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const handleStopStream = () => {
    abortControllerRef.current?.abort();
    isStreamingRef.current = false;
    setIsStreaming(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChat(inputPrompt);
    }
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <AppLayout>
      <div className="flex-1 flex flex-col h-full overflow-hidden relative" style={{ background: '#F7F4ED' }}>
        {/* Main Chat Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6">
          {messages.length === 0 && !isStreaming ? (
            /* Assistant UI Empty State */
            <EmptyState
              greeting="Ask AutoMind Anything About Cars"
              suggestions={SUGGESTIONS_LIST}
              onSelectSuggestion={(s) => sendChat(s)}
            />
          ) : (
            /* Render Saved & Past Messages */
            messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3.5 max-w-4xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                {/* Avatar Icon */}
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 shadow-sm"
                  style={{
                    background: msg.role === 'user' ? '#0D0D0D' : '#EFECE5',
                    color: msg.role === 'user' ? '#FFFFFF' : '#C96A2B',
                    border: msg.role === 'user' ? 'none' : '1px solid #E2DDD6'
                  }}
                >
                  {msg.role === 'user' ? 'U' : <Sparkles className="w-3.5 h-3.5" />}
                </div>

                {/* Bubble Container */}
                <div className={`space-y-3 max-w-3xl ${msg.role === 'user' ? 'text-right' : ''}`}>
                  <div
                    className="p-4 sm:p-5 rounded-2xl shadow-sm"
                    style={{
                      background: msg.role === 'user' ? '#0D0D0D' : '#FFFFFF',
                      color: msg.role === 'user' ? '#FFFFFF' : '#0D0D0D',
                      border: msg.role === 'user' ? 'none' : '1px solid #E2DDD6',
                    }}
                  >
                    {/* Header for Assistant Messages */}
                    {msg.role === 'assistant' && (
                      <div className="flex items-center justify-between mb-3 pb-2" style={{ borderBottom: '1px solid #E2DDD6' }}>
                        <span className="text-[11px] font-bold uppercase tracking-wider" style={{ color: '#C96A2B' }}>
                          AutoMind AI Analysis
                        </span>
                        <button
                          onClick={() => handleCopy(msg.content, idx)}
                          className="transition-colors"
                          style={{ color: '#9C9590' }}
                          title="Copy Answer"
                        >
                          {copiedIdx === idx ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    )}

                    {/* Content */}
                    <div className={msg.role === 'user' ? 'text-sm text-left font-medium' : 'chat-prose text-left'}>
                      {/* Vehicle Pricing Quote Card if present */}
                      {msg.role === 'assistant' && msg.metadata?.pricing_quote && (
                        <PricingQuoteCard quote={msg.metadata.pricing_quote} />
                      )}

                      {/* Vehicle Media Gallery if present */}
                      {msg.role === 'assistant' && msg.metadata?.gallery && (
                        <VehicleGalleryCard gallery={msg.metadata.gallery} />
                      )}

                      {msg.role === 'user' ? (
                        <p className="m-0 whitespace-pre-wrap">{msg.content}</p>
                      ) : (
                        <StreamingText text={msg.content} streaming={false} />
                      )}
                    </div>

                    {/* Feedback Rating Controls for Assistant Messages */}
                    {msg.role === 'assistant' && (
                      <MessageFeedback
                        conversationId={conversationId || msg.conversation_id || 0}
                        messageId={msg.id || (idx + 1)}
                        prompt={idx > 0 && messages[idx - 1]?.role === 'user' ? messages[idx - 1]?.content : undefined}
                        responseContent={msg.content}
                      />
                    )}
                  </div>


                </div>
              </motion.div>
            ))
          )}

          {/* Active Realtime SSE Streaming Response View */}
          {isStreaming && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4 max-w-4xl">
              {/* Assistant UI Thinking Indicator */}
              {!streamingText && (
                <ThinkingIndicator
                  label={STAGE_LABELS[currentStage] || currentStageMessage || "Thinking..."}
                />
              )}

              {/* Live Streaming Response with Cursor */}
              {streamingText && (
                <div className="flex gap-3.5 max-w-4xl">
                  <div
                    className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 shadow-sm"
                    style={{ background: '#EFECE5', color: '#C96A2B', border: '1px solid #E2DDD6' }}
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                  </div>

                  <div className="flex-1 space-y-4">
                    <div
                      className="p-4 sm:p-5 rounded-2xl shadow-sm"
                      style={{ background: '#FFFFFF', border: '1px solid #E2DDD6', color: '#0D0D0D' }}
                    >
                      {activePricingQuote && <PricingQuoteCard quote={activePricingQuote} />}
                      {activeGallery && <VehicleGalleryCard gallery={activeGallery} />}
                      <StreamingText text={streamingText} streaming={isStreaming} />
                    </div>


                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Follow-up Suggestions when settled */}
          {messages.length > 0 && !isStreaming && (
            <div className="pt-2">
              <Suggestions
                suggestions={[
                  "Compare safety ratings & airbags",
                  "What is the estimated on-road price?",
                  "Which websites should I check before buying?",
                  "Show EV vs Diesel cost analysis"
                ]}
                onSuggestion={(suggestion) => sendChat(suggestion)}
              />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Floating Input Composer Footer */}
        <div className="p-4" style={{ background: 'rgba(247,244,237,0.95)', backdropFilter: 'blur(12px)', borderTop: '1px solid #E2DDD6' }}>
          <div className="max-w-4xl mx-auto relative">
            <div
              className="rounded-full p-2 ps-4 pe-2.5 shadow-sm flex items-center justify-between gap-2.5"
              style={{ background: '#FFFFFF', border: '1px solid #E2DDD6' }}
            >
              <VoiceInputButton
                onTranscript={(text) => setInputPrompt(text)}
                disabled={isStreaming}
              />

              <textarea
                rows={1}
                value={inputPrompt}
                onChange={(e) => setInputPrompt(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything about cars (English, हिंदी, ગુજરાતી)..."
                className="flex-1 bg-transparent text-sm outline-none resize-none"
                style={{ color: '#0D0D0D' }}
              />

              {isStreaming ? (
                <button
                  onClick={handleStopStream}
                  className="flex size-8 items-center justify-center rounded-full text-white transition-colors shrink-0"
                  style={{ background: '#EF4444' }}
                >
                  <Square className="size-3.5" />
                </button>
              ) : (
                <button
                  onClick={() => sendChat(inputPrompt)}
                  disabled={!inputPrompt.trim()}
                  className="flex size-8 items-center justify-center rounded-full text-white transition-colors disabled:opacity-40 shrink-0 cursor-pointer"
                  style={{ background: '#0D0D0D' }}
                >
                  <ArrowUpIcon className="size-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
