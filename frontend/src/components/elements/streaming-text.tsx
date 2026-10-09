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
            <div className="my-3 overflow-x-auto rounded-xl border border-[#B7A89A] bg-[#FAF7F2] shadow-xs">
              <table className="w-full text-left text-xs border-collapse" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-[#E8DCC6] text-[#1A1614] font-semibold border-b border-[#B7A89A]" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="px-3.5 py-2.5 font-semibold text-[#1A1614] border-r border-[#B7A89A] last:border-r-0" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-3.5 py-2.5 text-[#2D2520] border-t border-[#B7A89A] border-r border-[#B7A89A] last:border-r-0 hover:bg-[#E8DCC6] transition-colors" {...props} />
          ),
          a: ({ node, href, children, ...props }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 font-medium text-[#722F37] hover:text-[#58242A] underline decoration-[#722F37]/40 underline-offset-3 transition-colors"
              {...props}
            >
              <span>{children}</span>
              <ExternalLink className="size-3 shrink-0 opacity-70" />
            </a>
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-base font-bold text-[#1A1614] mt-4 mb-2 pb-1 border-b border-[#B7A89A] flex items-center gap-2" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-sm font-semibold text-[#1A1614] mt-3 mb-1.5" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="my-2 space-y-1.5 list-disc list-inside text-[#2D2520]" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="my-2 space-y-1.5 list-decimal list-inside text-[#2D2520]" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="leading-snug" {...props} />
          ),
          img: ({ node, src, alt, ...props }) => (
            <div className="my-3 overflow-hidden rounded-xl border border-[#B7A89A] bg-[#FAF7F2] shadow-xs max-w-lg">
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
                <div className="px-3.5 py-2 text-xs text-[#5C524A] bg-[#E8DCC6] border-t border-[#B7A89A] font-medium flex items-center justify-between">
                  <span>📷 {alt}</span>
                </div>
              )}
            </div>
          ),
          code: ({ node, className, children, ...props }: any) => {
            const textContent = String(children);
            if (textContent.includes("Manufacturer Claim") || textContent.includes("manufacturer_claim")) {
              return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-300">🧪 {children}</span>;
            }
            if (textContent.includes("Independently Measured") || textContent.includes("independently_measured") || textContent.includes("Officially Recognized") || textContent.includes("officially_recognized_record")) {
              return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300">✅ {children}</span>;
            }
            if (textContent.includes("Estimated") || textContent.includes("estimated")) {
              return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-300">📊 {children}</span>;
            }
            return <code className="px-1.5 py-0.5 bg-[#DFD2BA] text-[#722F37] rounded font-mono text-xs" {...props}>{children}</code>;
          },
        }}
      >
        {cleanText}
      </ReactMarkdown>
      {streaming && (
        <span
          aria-hidden
          className="ml-1 inline-block h-4 w-1 animate-pulse rounded-full"
          style={{ background: '#722F37' }}
        />
      )}
    </div>
  );
}
