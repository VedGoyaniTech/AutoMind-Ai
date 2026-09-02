import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ExternalLink } from "lucide-react";

export interface Segment {
  text: string;
  mono?: boolean;
}

export function StreamingText({
  text,
  streaming,
  className,
}: {
  text: string;
  streaming: boolean;
  className?: string;
}) {
  const cleanText = useMemo(() => {
    if (!text) return "";
    // Fix glued headers (e.g. "Lakh## 🛡️ Header" -> "Lakh\n\n## 🛡️ Header"), ignoring table rows containing '|'
    let s = text.replace(/([^\n#|])(#{1,6}\s)/g, "$1\n\n$2");
    // Ensure newline before markdown list items if glued to end of line
    s = s.replace(/([^\n|])(\d+\.\s+\*\*)/g, "$1\n$2");
    return s;
  }, [text]);

  return (
    <div className={`chat-prose text-left text-sm leading-relaxed ${className || ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table: ({ node, ...props }) => (
            <div className="my-3 overflow-x-auto rounded-xl border border-[#E2DDD6] bg-white shadow-xs">
              <table className="w-full text-left text-xs border-collapse" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-[#F7F4ED] text-[#0D0D0D] font-semibold border-b border-[#E2DDD6]" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="px-3.5 py-2.5 font-semibold text-[#0D0D0D] border-r border-[#E2DDD6] last:border-r-0" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-3.5 py-2.5 text-[#333333] border-t border-[#E2DDD6] border-r border-[#E2DDD6] last:border-r-0 hover:bg-[#FAF8F5] transition-colors" {...props} />
          ),
          a: ({ node, href, children, ...props }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 font-medium text-[#C96A2B] hover:text-[#9A4C1B] underline decoration-[#C96A2B]/40 underline-offset-3 transition-colors"
              {...props}
            >
              <span>{children}</span>
              <ExternalLink className="size-3 shrink-0 opacity-70" />
            </a>
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-base font-bold text-[#0D0D0D] mt-4 mb-2 pb-1 border-b border-[#E2DDD6] flex items-center gap-2" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-sm font-semibold text-[#1A1A1A] mt-3 mb-1.5" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="my-2 space-y-1.5 list-disc list-inside text-[#333333]" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="my-2 space-y-1.5 list-decimal list-inside text-[#333333]" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="leading-snug" {...props} />
          ),
          img: ({ node, src, alt, ...props }) => (
            <div className="my-3 overflow-hidden rounded-xl border border-[#E2DDD6] bg-[#FAF8F5] shadow-xs max-w-lg">
              <img
                src={src}
                alt={alt || "Car Image"}
                className="w-full max-h-72 object-cover transition-transform duration-300 hover:scale-102"
                loading="lazy"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = 'none';
                }}
                {...props}
              />
              {alt && (
                <div className="px-3.5 py-2 text-xs text-[#555555] bg-[#F7F4ED] border-t border-[#E2DDD6] font-medium flex items-center justify-between">
                  <span>📷 {alt}</span>
                </div>
              )}
            </div>
          ),
        }}
      >
        {cleanText}
      </ReactMarkdown>
      {streaming && (
        <span
          aria-hidden
          className="ml-1 inline-block h-4 w-1 animate-pulse rounded-full"
          style={{ background: '#C96A2B' }}
        />
      )}
    </div>
  );
}
