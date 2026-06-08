import { Scale, User, BookOpen, Newspaper, ScrollText } from "lucide-react";
import { motion } from "motion/react";

export interface Citation {
  id: string;
  text: string;
  source: string;
  article?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
  onCitationClick?: (citation: Citation) => void;
  index?: number;
}

function CitationBadge({
  citation,
  onClick,
}: {
  citation: Citation;
  onClick?: () => void;
}) {
  const label = citation.article || citation.source;
  const isLaw = citation.source.includes("Luật") || citation.source.includes("Bộ luật");

  return (
    <motion.button
      whileHover={{ scale: 1.05, y: -1 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all"
      style={{
        background: isLaw
          ? "linear-gradient(135deg, rgba(79,70,229,0.12), rgba(124,58,237,0.12))"
          : "linear-gradient(135deg, rgba(16,185,129,0.12), rgba(5,150,105,0.12))",
        border: `1px solid ${isLaw ? "rgba(99,102,241,0.35)" : "rgba(16,185,129,0.35)"}`,
        color: isLaw ? "#6366f1" : "#059669",
      }}
    >
      {isLaw ? <BookOpen className="size-3" /> : <Newspaper className="size-3" />}
      {label}
    </motion.button>
  );
}

function parseContentWithBold(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

export function ChatMessage({ message, onCitationClick, index = 0 }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, x: isUser ? 15 : -15 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      transition={{
        duration: 0.35,
        ease: [0.16, 1, 0.3, 1],
        delay: Math.min(index * 0.05, 0.2),
      }}
      className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {/* Bot avatar */}
      {!isUser && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3, type: "spring", stiffness: 400 }}
          className="size-8 rounded-full flex items-center justify-center shrink-0 mt-1"
          style={{
            background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
            boxShadow: "0 4px 12px rgba(99,102,241,0.35)",
          }}
        >
          <Scale className="size-4 text-white" />
        </motion.div>
      )}

      <div className={`flex flex-col gap-2 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        {/* Message bubble */}
        {isUser ? (
          <motion.div
            whileHover={{ scale: 1.01 }}
            className="px-4 py-3 rounded-2xl rounded-tr-sm relative overflow-hidden"
            style={{
              background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
              boxShadow: "0 4px 20px rgba(99,102,241,0.35)",
            }}
          >
            <div className="animate-shimmer absolute inset-0 opacity-50" />
            <p className="text-sm text-white whitespace-pre-wrap relative z-10">
              {message.content}
            </p>
          </motion.div>
        ) : (
          <motion.div
            whileHover={{ scale: 1.005 }}
            className="px-4 py-3 rounded-2xl rounded-tl-sm"
            style={{
              background: "var(--card)",
              border: "1px solid var(--border)",
              boxShadow: "0 4px 20px rgba(0,0,0,0.06)",
            }}
          >
            {/* Decorative accent line */}
            <div
              className="absolute left-0 top-3 bottom-3 w-0.5 rounded-full"
              style={{
                background: "linear-gradient(to bottom, #6366f1, #a78bfa)",
                marginLeft: "-1px",
              }}
            />
            <div className="text-sm whitespace-pre-wrap" style={{ color: "var(--foreground)" }}>
              {message.content.split("\n").map((line, i) => (
                <p key={i} className={line === "" ? "h-2" : "mb-0.5"}>
                  {parseContentWithBold(line)}
                </p>
              ))}
            </div>
          </motion.div>
        )}

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="flex flex-wrap gap-1.5"
          >
            <span className="flex items-center gap-1 text-xs mr-1" style={{ color: "var(--muted-foreground)" }}>
              <ScrollText className="size-3" />
              Nguồn:
            </span>
            {message.citations.map((citation) => (
              <CitationBadge
                key={citation.id}
                citation={citation}
                onClick={() => onCitationClick?.(citation)}
              />
            ))}
          </motion.div>
        )}

        {/* Timestamp */}
        <span className="text-xs px-1" style={{ color: "var(--muted-foreground)", opacity: 0.7 }}>
          {message.timestamp.toLocaleTimeString("vi-VN", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>

      {/* User avatar */}
      {isUser && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3, type: "spring", stiffness: 400 }}
          className="size-8 rounded-full flex items-center justify-center shrink-0 mt-1"
          style={{
            background: "linear-gradient(135deg, #e0e7ff, #ede9fe)",
            border: "1px solid rgba(99,102,241,0.25)",
          }}
        >
          <User className="size-4" style={{ color: "#6366f1" }} />
        </motion.div>
      )}
    </motion.div>
  );
}
