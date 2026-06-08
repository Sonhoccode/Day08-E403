import { useState, useRef, useEffect } from "react";
import { Scale, Trash2, Sun, Moon, Sparkles, Shield } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { ChatMessage, Message } from "./components/ChatMessage";
import { ChatInput } from "./components/ChatInput";
import { SourceDocuments, SourceDocument } from "./components/SourceDocuments";
import { SuggestedQuestions } from "./components/SuggestedQuestions";
import { Button } from "./components/ui/button";
import { ScrollArea } from "./components/ui/scroll-area";
import {
  generateMockResponse,
  buildConversationMemory,
  simulateAPICall,
  suggestedQuestions,
} from "./utils/mockData";
import { useTheme } from "next-themes";

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3 justify-start"
    >
      <div
        className="size-8 rounded-full flex items-center justify-center shrink-0"
        style={{
          background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
          boxShadow: "0 4px 12px rgba(99,102,241,0.35)",
        }}
      >
        <Scale className="size-4 text-white" />
      </div>
      <div
        className="px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-1.5"
        style={{
          background: "var(--card)",
          border: "1px solid var(--border)",
          boxShadow: "0 4px 20px rgba(0,0,0,0.06)",
        }}
      >
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="size-2 rounded-full"
            style={{ background: "#6366f1" }}
            animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </div>
    </motion.div>
  );
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sourceDocuments, setSourceDocuments] = useState<SourceDocument[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [highlightedSourceId, setHighlightedSourceId] = useState<string>();
  const [conversationMemory, setConversationMemory] = useState("Chưa có lịch sử hội thoại.");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { theme, setTheme } = useTheme();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
    setConversationMemory(buildConversationMemory(messages).summary);
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const memorySnapshot = buildConversationMemory([...messages, userMessage]);
      const response = generateMockResponse(content, memorySnapshot);
      const assistantMessage = await simulateAPICall(content, memorySnapshot);
      setMessages((prev) => [...prev, assistantMessage]);
      setSourceDocuments((prev) => {
        const existingIds = new Set(prev.map((doc) => doc.id));
        const newDocs = response.sources.filter((doc) => !existingIds.has(doc.id));
        return [...prev, ...newDocs];
      });
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCitationClick = (citation: { id: string; source: string }) => {
    const sourceDoc = sourceDocuments.find(
      (doc) => doc.title.includes(citation.source) || citation.source.includes(doc.title)
    );
    if (sourceDoc) {
      setHighlightedSourceId(sourceDoc.id);
      setTimeout(() => setHighlightedSourceId(undefined), 3000);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setSourceDocuments([]);
  };

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const isDark = theme === "dark";

  return (
    <div className="size-full flex flex-col relative overflow-hidden" style={{ background: "var(--background)" }}>
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.15, 0.25, 0.15] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-40 -left-40 w-96 h-96 rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, #6366f1, transparent)" }}
        />
        <motion.div
          animate={{ scale: [1, 1.15, 1], opacity: [0.12, 0.2, 0.12] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute top-1/3 -right-20 w-80 h-80 rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, #a78bfa, transparent)" }}
        />
        <motion.div
          animate={{ scale: [1, 1.08, 1], opacity: [0.08, 0.15, 0.08] }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 4 }}
          className="absolute -bottom-20 left-1/3 w-72 h-72 rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, #818cf8, transparent)" }}
        />
      </div>

      {/* Header */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 border-b"
        style={{
          background: isDark ? "rgba(15, 22, 41, 0.85)" : "rgba(255, 255, 255, 0.85)",
          backdropFilter: "blur(20px)",
          borderColor: "var(--border)",
        }}
      >
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <motion.div
                whileHover={{ scale: 1.05, rotate: 3 }}
                whileTap={{ scale: 0.95 }}
                className="relative p-2.5 rounded-xl overflow-hidden cursor-pointer"
                style={{
                  background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                  boxShadow: "0 4px 15px rgba(99, 102, 241, 0.4)",
                }}
              >
                <div className="animate-shimmer absolute inset-0 rounded-xl" />
                <Scale className="size-6 text-white relative z-10" />
              </motion.div>

              <div>
                <div className="flex items-center gap-2">
                  <h1
                    className="font-semibold"
                    style={{
                      background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
                      WebkitBackgroundClip: "text",
                      WebkitTextFillColor: "transparent",
                    }}
                  >
                    Chatbot Pháp Luật Ma Túy
                  </h1>
                  <span
                    className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                    style={{
                      background: "linear-gradient(135deg, rgba(99,102,241,0.12), rgba(124,58,237,0.12))",
                      color: "#6366f1",
                      border: "1px solid rgba(99,102,241,0.3)",
                    }}
                  >
                    <Sparkles className="size-3" />
                    AI
                  </span>
                </div>
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                  Hỗ trợ tra cứu và tư vấn pháp luật về ma túy
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div
                className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium"
                style={{
                  background: "rgba(34, 197, 94, 0.08)",
                  border: "1px solid rgba(34, 197, 94, 0.25)",
                  color: "#16a34a",
                }}
              >
                <motion.span
                  animate={{ scale: [1, 1.4, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="size-1.5 rounded-full bg-green-500"
                />
                Trực tuyến
              </div>

              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={toggleTheme}
                  className="rounded-xl"
                  style={{ borderColor: "var(--border)" }}
                >
                  {isDark ? (
                    <Sun className="size-4 text-amber-400" />
                  ) : (
                    <Moon className="size-4" style={{ color: "#6366f1" }} />
                  )}
                </Button>
              </motion.div>

              <AnimatePresence>
                {messages.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, x: 10, scale: 0.9 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    exit={{ opacity: 0, x: 10, scale: 0.9 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      variant="outline"
                      onClick={handleClearChat}
                      className="gap-2 rounded-xl"
                      style={{
                        borderColor: "rgba(239,68,68,0.3)",
                        color: "#ef4444",
                        background: "rgba(239,68,68,0.04)",
                      }}
                    >
                      <Trash2 className="size-4" />
                      <span className="hidden sm:inline">Xóa hội thoại</span>
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden relative z-10">
        <div className="container mx-auto px-4 h-full">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-full py-4">
            {/* Chat Area */}
            <div className="lg:col-span-2 flex flex-col h-full">
              <ScrollArea className="flex-1 pr-2">
                <AnimatePresence mode="wait">
                  {messages.length === 0 ? (
                    <motion.div
                      key="welcome"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.4 }}
                      className="flex flex-col items-center justify-center min-h-[400px] gap-8 py-12"
                    >
                      {/* Hero icon */}
                      <motion.div
                        animate={{ y: [0, -8, 0] }}
                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                        className="relative"
                      >
                        <div
                          className="p-6 rounded-3xl relative overflow-hidden"
                          style={{
                            background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                            boxShadow: "0 20px 60px rgba(99, 102, 241, 0.4)",
                          }}
                        >
                          <div className="animate-shimmer absolute inset-0 rounded-3xl" />
                          <Scale className="size-14 text-white relative z-10" />
                        </div>
                        <motion.div
                          animate={{ scale: [1, 1.1, 1], opacity: [0.2, 0.3, 0.2] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="absolute -inset-4 rounded-3xl"
                          style={{ border: "2px solid #6366f1" }}
                        />
                        <motion.div
                          animate={{ scale: [1, 1.08, 1], opacity: [0.08, 0.15, 0.08] }}
                          transition={{ duration: 2.5, repeat: Infinity, delay: 0.5 }}
                          className="absolute -inset-8 rounded-3xl"
                          style={{ border: "2px solid #6366f1" }}
                        />
                      </motion.div>

                      <div className="text-center space-y-3 max-w-lg px-4">
                        <h2
                          className="font-semibold"
                          style={{
                            background: "linear-gradient(135deg, #4f46e5, #7c3aed, #a78bfa)",
                            WebkitBackgroundClip: "text",
                            WebkitTextFillColor: "transparent",
                          }}
                        >
                          Chào mừng đến với Chatbot Pháp Luật Ma Túy
                        </h2>
                        <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                          Tôi có thể giúp bạn tra cứu thông tin về pháp luật ma túy,
                          các quy định liên quan và tin tức mới nhất với trích dẫn chính xác.
                        </p>
                        <div className="flex flex-wrap justify-center gap-2 pt-1">
                          {[
                            { icon: Shield, label: "Chính xác & Đáng tin cậy" },
                            { icon: Scale, label: "Trích dẫn pháp luật" },
                            { icon: Sparkles, label: "AI thông minh" },
                          ].map(({ icon: Icon, label }, i) => (
                            <motion.span
                              key={label}
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: 0.3 + i * 0.1 }}
                              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs"
                              style={{
                                background: "rgba(99,102,241,0.08)",
                                border: "1px solid rgba(99,102,241,0.2)",
                                color: "#6366f1",
                              }}
                            >
                              <Icon className="size-3" />
                              {label}
                            </motion.span>
                          ))}
                        </div>
                      </div>

                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="w-full max-w-2xl"
                      >
                        <SuggestedQuestions
                          questions={suggestedQuestions}
                          onQuestionClick={handleSendMessage}
                        />
                      </motion.div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="messages"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="space-y-2 pb-4 pt-2"
                    >
                      {messages.map((message, index) => (
                        <ChatMessage
                          key={message.id}
                          message={message}
                          onCitationClick={handleCitationClick}
                          index={index}
                        />
                      ))}
                      {isLoading && <TypingIndicator />}
                      <div ref={messagesEndRef} />
                    </motion.div>
                  )}
                </AnimatePresence>
              </ScrollArea>

              {/* Input Area */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="mt-3 p-3 rounded-2xl"
                style={{
                  background: isDark ? "rgba(15, 22, 41, 0.6)" : "rgba(255, 255, 255, 0.8)",
                  backdropFilter: "blur(12px)",
                  border: "1px solid var(--border)",
                  boxShadow: "0 -4px 20px rgba(99,102,241,0.06)",
                }}
              >
                <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
                <div
                  className="mt-2 text-xs rounded-xl px-3 py-2"
                  style={{
                    background: "rgba(99,102,241,0.06)",
                    border: "1px solid rgba(99,102,241,0.15)",
                    color: "var(--muted-foreground)",
                  }}
                >
                  <span className="font-medium" style={{ color: "var(--foreground)" }}>
                    Bộ nhớ hội thoại:
                  </span>{" "}
                  {conversationMemory}
                </div>
              </motion.div>
            </div>

            {/* Source Documents Sidebar */}
            <div className="lg:col-span-1 h-full hidden lg:block">
              <SourceDocuments
                documents={sourceDocuments}
                highlightedId={highlightedSourceId}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
