import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Globe, AlertCircle, CheckCircle2, X } from 'lucide-react';
import api from '../../api/client';

interface VoiceInputButtonProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export type SupportedLanguage = 'hi-IN' | 'gu-IN' | 'en-IN';

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  onTranscript,
  disabled = false
}) => {
  const [isListening, setIsListening] = useState(false);
  const [selectedLang, setSelectedLang] = useState<SupportedLanguage>(() => {
    return (localStorage.getItem('automind_voice_lang') as SupportedLanguage) || 'hi-IN';
  });
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [interimPreview, setInterimPreview] = useState<string>('');
  const [recordSeconds, setRecordSeconds] = useState(0);

  const recognitionRef = useRef<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<any>(null);
  const finalTranscriptRef = useRef<string>('');

  const handleLanguageChange = (lang: SupportedLanguage) => {
    setSelectedLang(lang);
    localStorage.setItem('automind_voice_lang', lang);
    setShowLangMenu(false);
    if (isListening) {
      stopListening();
    }
  };

  // Upload audio to server-side transcription fallback if browser speech recognition fails
  const sendAudioToServerFallback = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      formData.append('language', selectedLang);

      const res = await api.post('/voice/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (res.data && res.data.transcript) {
        const text = res.data.transcript;
        onTranscript(text);
      }
    } catch (e) {
      console.warn('Server audio fallback notice:', e);
    }
  };

  // Stop recording cleanly
  const stopListening = useCallback(() => {
    setIsListening(false);
    clearInterval(timerRef.current);
    setRecordSeconds(0);

    // Stop Web Speech Recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
    }

    // Stop MediaRecorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch (_) {}
    }

    const captured = finalTranscriptRef.current.trim();
    if (captured) {
      onTranscript(captured);
    }
    setInterimPreview('');
  }, [onTranscript]);

  // Start speech recognition & MediaRecorder fallback
  const startListening = async () => {
    setErrorMessage(null);
    setInterimPreview('');
    finalTranscriptRef.current = '';
    audioChunksRef.current = [];

    // 1. Initialize MediaRecorder audio capture as backup
    let mediaStream: MediaStream | null = null;
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(mediaStream);
        recorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };
        recorder.onstop = () => {
          mediaStream?.getTracks().forEach((t) => t.stop());
          if (!finalTranscriptRef.current && audioChunksRef.current.length > 0) {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            sendAudioToServerFallback(audioBlob);
          }
        };
        recorder.start(500);
        mediaRecorderRef.current = recorder;
      } catch (micErr: any) {
        if (micErr.name === 'NotAllowedError' || micErr.name === 'PermissionDeniedError') {
          setErrorMessage('Microphone blocked. Please click 🔒 in URL address bar to allow microphone access.');
          return;
        }
      }
    }

    // 2. Initialize Browser Speech Recognition
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = selectedLang;

        recognition.onstart = () => {
          setIsListening(true);
        };

        recognition.onresult = (event: any) => {
          let accumulated = '';
          for (let i = 0; i < event.results.length; i++) {
            const text = event.results[i][0]?.transcript || '';
            accumulated += text + ' ';
          }
          const cleanText = accumulated.trim();
          if (cleanText) {
            finalTranscriptRef.current = cleanText;
            setInterimPreview(cleanText);
            // Pass clean current transcript directly (without duplicating)
            onTranscript(cleanText);
          }
        };

        recognition.onerror = (event: any) => {
          console.warn('Speech recognition notice:', event.error);
          if (event.error === 'not-allowed') {
            setErrorMessage('Microphone blocked. Click 🔒 in address bar to allow mic.');
          } else if (event.error === 'audio-capture') {
            setErrorMessage('Microphone busy or not detected.');
          }
        };

        recognition.onend = () => {
          if (isListening) {
            stopListening();
          }
        };

        recognitionRef.current = recognition;
        recognition.start();
      } catch (e) {
        console.warn('SpeechRecognition start notice:', e);
      }
    }

    setIsListening(true);
    setRecordSeconds(0);
    timerRef.current = setInterval(() => {
      setRecordSeconds((prev) => {
        if (prev >= 15) {
          stopListening();
          return 0;
        }
        return prev + 1;
      });
    }, 1000);
  };

  const langLabels: Record<SupportedLanguage, { name: string; native: string }> = {
    'hi-IN': { name: 'Hindi', native: 'हिंदी' },
    'gu-IN': { name: 'Gujarati', native: 'ગુજરાતી' },
    'en-IN': { name: 'English', native: 'English' }
  };

  return (
    <div className="relative flex items-center gap-1.5 shrink-0">
      {/* Main Microphone Button */}
      <button
        type="button"
        onClick={isListening ? stopListening : startListening}
        disabled={disabled}
        aria-label={isListening ? 'Stop recording voice' : 'Speak your car question in Hindi, Gujarati or English'}
        title={isListening ? 'Listening... Click to finish' : `Voice Input (${langLabels[selectedLang].native})`}
        className={`relative p-2.5 rounded-full transition-all duration-300 flex items-center justify-center cursor-pointer ${
          isListening
            ? 'bg-rose-600 text-white shadow-lg shadow-rose-600/50 ring-4 ring-rose-500/25 scale-105'
            : 'bg-zinc-100 hover:bg-zinc-200 text-zinc-700 hover:text-zinc-900 border border-zinc-300'
        } ${disabled ? 'opacity-40 cursor-not-allowed' : ''}`}
      >
        {isListening ? (
          <>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
            </span>
            <Mic className="w-4 h-4 animate-pulse" />
          </>
        ) : (
          <Mic className="w-4 h-4 text-zinc-700" />
        )}
      </button>

      {/* Language Selector Trigger Button */}
      <button
        type="button"
        onClick={() => setShowLangMenu(!showLangMenu)}
        title="Select Speaking Language"
        className="px-2 py-1 text-[11px] font-semibold tracking-wider text-zinc-700 hover:text-zinc-900 bg-zinc-100 hover:bg-zinc-200 border border-zinc-300 rounded-lg flex items-center gap-1 transition cursor-pointer"
      >
        <Globe className="w-3 h-3 text-zinc-500" />
        <span className="uppercase">{selectedLang.split('-')[0]}</span>
      </button>

      {/* Realtime Spoken Text Preview Pill */}
      {isListening && (
        <div className="absolute bottom-12 left-0 z-50 flex items-center gap-2 bg-zinc-900/95 text-white px-3.5 py-1.5 rounded-full text-xs shadow-xl backdrop-blur-md border border-zinc-700 whitespace-nowrap animate-in fade-in">
          <span className="size-2 rounded-full bg-rose-500 animate-ping shrink-0" />
          <span className="text-zinc-300">Listening ({recordSeconds}s):</span>
          <span className="font-medium max-w-xs truncate text-amber-300">
            {interimPreview || 'Speak now...'}
          </span>
          <button
            type="button"
            onClick={stopListening}
            className="ml-1 text-[10px] bg-rose-600 hover:bg-rose-500 text-white px-2 py-0.5 rounded-full font-bold transition cursor-pointer"
          >
            Done
          </button>
        </div>
      )}

      {/* Clean Language Selector Popover (ONLY Language Selection) */}
      {showLangMenu && (
        <div className="absolute bottom-12 left-0 z-50 w-52 bg-white border border-zinc-200 rounded-2xl shadow-xl p-2 text-xs text-zinc-800 animate-in fade-in zoom-in-95">
          <div className="flex items-center justify-between px-2 py-1.5 border-b border-zinc-100 mb-1">
            <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">
              Select Language
            </span>
            <button
              onClick={() => setShowLangMenu(false)}
              className="text-zinc-400 hover:text-zinc-600 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-1">
            {(['hi-IN', 'gu-IN', 'en-IN'] as SupportedLanguage[]).map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => handleLanguageChange(lang)}
                className={`w-full text-left px-3 py-2 rounded-xl flex items-center justify-between transition cursor-pointer ${
                  selectedLang === lang
                    ? 'bg-zinc-900 text-white font-medium shadow-sm'
                    : 'hover:bg-zinc-100 text-zinc-700'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">{langLabels[lang].native}</span>
                  <span className={`text-[11px] ${selectedLang === lang ? 'text-zinc-300' : 'text-zinc-400'}`}>
                    ({langLabels[lang].name})
                  </span>
                </div>
                {selectedLang === lang && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Floating Error Toast */}
      {errorMessage && (
        <div className="absolute bottom-14 left-0 z-50 bg-zinc-900 text-zinc-100 border border-zinc-700 px-3.5 py-2 rounded-xl text-xs flex items-center gap-2 shadow-2xl max-w-xs sm:max-w-md whitespace-normal">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
          <span className="leading-snug">{errorMessage}</span>
          <button
            onClick={() => setErrorMessage(null)}
            className="ml-auto text-zinc-400 hover:text-white cursor-pointer"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      )}
    </div>
  );
};
