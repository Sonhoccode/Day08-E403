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
      className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium transition-colors border"
      style={{
        background: "var(--muted)",
        borderColor: "var(--border)",
        color: "var(--foreground)",
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
          className="size-8 flex items-center justify-center shrink-0 mt-1"
          style={{
            background: "var(--primary)",
            color: "var(--primary-foreground)",
          }}
        >
          <Scale className="size-4" />
        </motion.div>
      )}

      <div className={`flex flex-col gap-2 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        {/* Message bubble */}
        {isUser ? (
          <motion.div
            className="px-4 py-3 relative overflow-hidden"
            style={{
              background: "var(--foreground)",
              color: "var(--background)",
            }}
          >
            <p className="text-sm whitespace-pre-wrap relative z-10">
              {message.content}
            </p>
          </motion.div>
        ) : (
          <motion.div
            className="relative px-4 py-3 overflow-hidden border"
            style={{
              background: "var(--card)",
              borderColor: "var(--border)",
            }}
          >
            {/* Decorative accent line */}
            <div
              className="absolute left-0 top-0 bottom-0 w-1"
              style={{
                background: "var(--primary)",
              }}
            />
            <div className="text-sm whitespace-pre-wrap pl-1" style={{ color: "var(--foreground)" }}>
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
          className="size-8 flex items-center justify-center shrink-0 mt-1 border"
          style={{
            background: "var(--muted)",
            borderColor: "var(--border)",
          }}
        >
          <User className="size-4" style={{ color: "var(--foreground)" }} />
        </motion.div>
      )}
    </motion.div>
  );
}
