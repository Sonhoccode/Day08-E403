import { useState, useRef, useEffect } from "react";
import { Scale, Trash2, Sun, Moon, Shield, ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { ChatMessage, Message } from "./components/ChatMessage";
import { ChatInput } from "./components/ChatInput";
import { SourceDocuments, SourceDocument } from "./components/SourceDocuments";
import { SuggestedQuestions } from "./components/SuggestedQuestions";
import { Button } from "./components/ui/button";
import { ScrollArea } from "./components/ui/scroll-area";
import {
  buildConversationMemory,
  suggestedQuestions,
} from "./utils/mockData";
import { sendChatMessage } from "./utils/ragApi";
import { useTheme } from "next-themes";

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3 justify-start"
    >
      <div className="size-8 flex items-center justify-center shrink-0 bg-primary text-primary-foreground">
        <Scale className="size-4" />
      </div>
      <div className="px-4 py-3 flex items-center gap-1.5 border bg-card">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="size-2 bg-primary"
            animate={{ opacity: [0.3, 1, 0.3] }}
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

  // Force light theme initially if it's not set
  useEffect(() => {
    if (theme !== 'light' && theme !== 'dark') {
      setTheme('light');
    }
  }, [theme, setTheme]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
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
    setConversationMemory(buildConversationMemory([...messages, userMessage]).summary);

    try {
      const history = [...messages, userMessage].map((message) => ({
        role: message.role,
        content: message.content,
      }));
      const response = await sendChatMessage(content, history, 5);
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setSourceDocuments((prev) => {
        const existingIds = new Set(prev.map((doc) => doc.id));
        const newDocs = response.sources.filter((doc) => !existingIds.has(doc.id));
        return [...prev, ...newDocs];
      });
      setConversationMemory(response.memory_summary);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "Không thể kết nối tới RAG API. Kiểm tra backend `group_project/app.py` và thử lại.",
          timestamp: new Date(),
        },
      ]);
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
    setConversationMemory("Chưa có lịch sử hội thoại.");
  };

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const isDark = theme === "dark";

  return (
    <div className="h-screen bg-background text-foreground flex flex-col font-sans selection:bg-primary selection:text-primary-foreground overflow-hidden">
      {/* Navbar Minimal */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 shrink-0">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold tracking-tight text-lg">
            <Scale className="size-5" />
            <span>Pháp Luật Ma Túy</span>
          </div>
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearChat}
                className="rounded-none border-destructive/30 text-destructive hover:bg-destructive/10 hidden sm:flex"
                aria-label="Clear chat"
              >
                <Trash2 className="size-4 mr-2" />
                Xóa lịch sử
              </Button>
            )}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 text-xs font-semibold border border-green-500/30 text-green-600 dark:text-green-400 rounded-none bg-green-500/10">
              <span className="size-1.5 bg-green-500 rounded-full animate-pulse" />
              Sẵn sàng
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={toggleTheme}
              className="rounded-none border-border"
              aria-label="Toggle theme"
            >
              {isDark ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="flex-1 min-h-0 flex overflow-hidden container mx-auto px-2 py-4 sm:px-4">
        <div className="w-full flex gap-4">
          {/* Chat Column */}
          <div className="flex-1 flex flex-col min-w-0 border border-border bg-card">
            <div className="flex-1 overflow-hidden">
              <ScrollArea className="h-full pr-4 p-4">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-12">
                    <Scale className="size-12 text-muted-foreground/30" />
                    <div>
                      <h3 className="font-medium text-lg">Bạn cần hỗ trợ gì?</h3>
                      <p className="text-sm text-muted-foreground mt-1">Chọn một câu hỏi gợi ý hoặc nhập câu hỏi của bạn.</p>
                    </div>
                    <div className="w-full max-w-xl">
                      <SuggestedQuestions
                        questions={suggestedQuestions}
                        onQuestionClick={handleSendMessage}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4 pb-4">
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
                  </div>
                )}
              </ScrollArea>
            </div>
            
            <div className="border-t border-border p-4 bg-muted/30">
              <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
              <div className="mt-3 text-xs text-muted-foreground">
                <span className="font-semibold text-foreground">Bộ nhớ:</span> {conversationMemory}
              </div>
            </div>
          </div>

          {/* Sources Area (Visible on large screens) */}
          <div className="hidden lg:block w-[360px] min-w-[360px] border border-border bg-card">
            <SourceDocuments
              documents={sourceDocuments}
              highlightedId={highlightedSourceId}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
