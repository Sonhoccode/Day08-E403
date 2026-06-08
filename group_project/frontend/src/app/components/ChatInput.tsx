import { useState, FormEvent, KeyboardEvent, useRef } from "react";
import { Send, Loader2, Mic } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSendMessage,
  isLoading = false,
  placeholder = "Nhập câu hỏi của bạn về pháp luật ma túy...",
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
  };

  const canSend = input.trim() && !isLoading;

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <div
        className="flex-1 flex items-end gap-2 px-4 py-2 transition-all duration-200 border bg-background"
        style={{
          borderColor: isFocused ? "var(--foreground)" : "var(--border)",
        }}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          disabled={isLoading}
          rows={1}
          className="flex-1 resize-none bg-transparent outline-none text-sm py-1.5 min-h-[36px] max-h-[120px]"
          style={{
            color: "var(--foreground)",
            lineHeight: "1.5",
          }}
        />
      </div>

      {/* Send button */}
      <motion.button
        type="submit"
        disabled={!canSend}
        aria-label="Gửi câu hỏi"
        className="size-[46px] flex items-center justify-center shrink-0 transition-colors duration-200 border"
        style={{
          background: canSend ? "var(--foreground)" : "var(--muted)",
          borderColor: canSend ? "var(--foreground)" : "var(--border)",
          color: canSend ? "var(--background)" : "var(--muted-foreground)",
          cursor: canSend ? "pointer" : "not-allowed",
        }}
      >
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
            >
              <Loader2 className="size-5 animate-spin" />
            </motion.div>
          ) : (
            <motion.div
              key="send"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
            >
              <Send className="size-5" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </form>
  );
}
