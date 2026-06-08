import { FileText, ExternalLink, BookOpen, Newspaper, Scale, Library } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { ScrollArea } from "./ui/scroll-area";

export interface SourceDocument {
  id: string;
  title: string;
  type: "law" | "news" | "regulation";
  article?: string;
  excerpt: string;
  url?: string;
  date?: string;
}

interface SourceDocumentsProps {
  documents: SourceDocument[];
  highlightedId?: string;
}

const typeConfig = {
  law: {
    label: "Văn bản pháp luật",
    icon: Scale,
    gradient: "linear-gradient(135deg, #4f46e5, #6366f1)",
    bg: "rgba(79,70,229,0.08)",
    border: "rgba(99,102,241,0.25)",
    color: "#4f46e5",
    badgeBg: "rgba(79,70,229,0.1)",
    badgeColor: "#4f46e5",
    badgeBorder: "rgba(79,70,229,0.3)",
  },
  news: {
    label: "Tin tức",
    icon: Newspaper,
    gradient: "linear-gradient(135deg, #059669, #10b981)",
    bg: "rgba(5,150,105,0.08)",
    border: "rgba(16,185,129,0.25)",
    color: "#059669",
    badgeBg: "rgba(16,185,129,0.1)",
    badgeColor: "#059669",
    badgeBorder: "rgba(16,185,129,0.3)",
  },
  regulation: {
    label: "Quy định",
    icon: BookOpen,
    gradient: "linear-gradient(135deg, #7c3aed, #a78bfa)",
    bg: "rgba(124,58,237,0.08)",
    border: "rgba(167,139,250,0.25)",
    color: "#7c3aed",
    badgeBg: "rgba(124,58,237,0.1)",
    badgeColor: "#7c3aed",
    badgeBorder: "rgba(124,58,237,0.3)",
  },
};

export function SourceDocuments({ documents, highlightedId }: SourceDocumentsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="h-full flex flex-col rounded-2xl overflow-hidden"
      style={{
        background: "var(--card)",
        border: "1px solid var(--border)",
        boxShadow: "0 4px 30px rgba(0,0,0,0.06)",
      }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 border-b flex items-center gap-3"
        style={{
          borderColor: "var(--border)",
          background: "rgba(99,102,241,0.04)",
        }}
      >
        <div
          className="p-2 rounded-lg"
          style={{
            background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
            boxShadow: "0 2px 8px rgba(99,102,241,0.3)",
          }}
        >
          <Library className="size-4 text-white" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
              Tài liệu nguồn
            </h3>
            <AnimatePresence>
              {documents.length > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  className="px-2 py-0.5 rounded-full text-xs font-semibold"
                  style={{
                    background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
                    color: "white",
                  }}
                >
                  {documents.length}
                </motion.span>
              )}
            </AnimatePresence>
          </div>
          <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
            Văn bản và tài liệu tham khảo
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {documents.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="h-full flex flex-col items-center justify-center gap-4 p-6 text-center"
          >
            <motion.div
              animate={{ y: [0, -5, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="p-5 rounded-2xl"
              style={{
                background: "rgba(99,102,241,0.08)",
                border: "1px dashed rgba(99,102,241,0.3)",
              }}
            >
              <FileText className="size-10" style={{ color: "#6366f1", opacity: 0.5 }} />
            </motion.div>
            <div>
              <p className="text-sm font-medium" style={{ color: "var(--foreground)" }}>
                Chưa có tài liệu
              </p>
              <p className="text-xs mt-1" style={{ color: "var(--muted-foreground)" }}>
                Đặt câu hỏi để xem các tài liệu nguồn được sử dụng
              </p>
            </div>
          </motion.div>
        ) : (
          <ScrollArea className="h-full">
            <div className="p-3 space-y-2">
              <AnimatePresence>
                {documents.map((doc, index) => {
                  const config = typeConfig[doc.type];
                  const Icon = config.icon;
                  const isHighlighted = highlightedId === doc.id;

                  return (
                    <motion.div
                      key={doc.id}
                      initial={{ opacity: 0, y: 10, x: 10 }}
                      animate={{
                        opacity: 1,
                        y: 0,
                        x: 0,
                        scale: isHighlighted ? 1.02 : 1,
                      }}
                      transition={{
                        delay: index * 0.06,
                        scale: { duration: 0.2 },
                      }}
                      whileHover={{ scale: 1.01, y: -1 }}
                      className="relative rounded-xl p-3 overflow-hidden transition-all"
                      style={{
                        background: isHighlighted
                          ? `linear-gradient(135deg, ${config.bg}, rgba(99,102,241,0.05))`
                          : "var(--card)",
                        border: `1px solid ${isHighlighted ? config.border : "var(--border)"}`,
                        boxShadow: isHighlighted
                          ? `0 0 0 2px ${config.color}30, 0 4px 20px rgba(0,0,0,0.06)`
                          : "0 1px 8px rgba(0,0,0,0.04)",
                      }}
                    >
                      {/* Colored left accent bar */}
                      <div
                        className="absolute left-0 top-0 bottom-0 w-0.5 rounded-l-xl"
                        style={{ background: config.gradient }}
                      />

                      <div className="pl-2">
                        {/* Type badge and external link */}
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span
                              className="flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium"
                              style={{
                                background: config.badgeBg,
                                color: config.badgeColor,
                                border: `1px solid ${config.badgeBorder}`,
                              }}
                            >
                              <Icon className="size-3" />
                              {config.label}
                            </span>
                            {doc.article && (
                              <span
                                className="px-2 py-0.5 rounded-md text-xs font-medium"
                                style={{
                                  background: "var(--muted)",
                                  color: "var(--muted-foreground)",
                                }}
                              >
                                {doc.article}
                              </span>
                            )}
                          </div>
                          {doc.url && (
                            <motion.a
                              href={doc.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              whileHover={{ scale: 1.2 }}
                              className="shrink-0"
                              style={{ color: config.color, opacity: 0.7 }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ExternalLink className="size-3.5" />
                            </motion.a>
                          )}
                        </div>

                        {/* Title */}
                        <h4 className="text-xs font-semibold leading-snug mb-1.5" style={{ color: "var(--foreground)" }}>
                          {doc.title}
                        </h4>

                        {/* Excerpt */}
                        <p className="text-xs leading-relaxed line-clamp-2" style={{ color: "var(--muted-foreground)" }}>
                          {doc.excerpt}
                        </p>

                        {/* Date */}
                        {doc.date && (
                          <p className="text-xs mt-2 font-medium" style={{ color: config.color, opacity: 0.8 }}>
                            {doc.date}
                          </p>
                        )}
                      </div>

                      {/* Highlight pulse effect */}
                      {isHighlighted && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: [0, 0.15, 0] }}
                          transition={{ duration: 1.5, repeat: 2 }}
                          className="absolute inset-0 rounded-xl pointer-events-none"
                          style={{ background: config.gradient }}
                        />
                      )}
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          </ScrollArea>
        )}
      </div>
    </motion.div>
  );
}
