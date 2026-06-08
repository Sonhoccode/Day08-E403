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
  },
  news: {
    label: "Tin tức",
    icon: Newspaper,
  },
  regulation: {
    label: "Quy định",
    icon: BookOpen,
  },
};

export function SourceDocuments({ documents, highlightedId }: SourceDocumentsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="h-full flex flex-col border"
      style={{
        background: "var(--card)",
        borderColor: "var(--border)",
      }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 border-b flex items-center gap-3 bg-muted"
        style={{
          borderColor: "var(--border)",
        }}
      >
        <div
          className="p-2 border bg-background"
          style={{
            borderColor: "var(--border)",
          }}
        >
          <Library className="size-4 text-foreground" />
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
                  className="px-2 py-0.5 text-xs font-semibold bg-foreground text-background"
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
              className="p-5 border bg-muted"
            >
              <FileText className="size-10 text-muted-foreground opacity-50" />
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
                      className="relative p-3 overflow-hidden transition-all border"
                      style={{
                        background: "var(--card)",
                        borderColor: isHighlighted ? "var(--foreground)" : "var(--border)",
                      }}
                    >
                      {/* Left accent bar for highlighted */}
                      {isHighlighted && (
                        <div
                          className="absolute left-0 top-0 bottom-0 w-1 bg-foreground"
                        />
                      )}

                      <div className={isHighlighted ? "pl-2" : ""}>
                        {/* Type badge and external link */}
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span
                              className="flex items-center gap-1 px-2 py-0.5 text-xs font-medium border bg-muted"
                            >
                              <Icon className="size-3" />
                              {config.label}
                            </span>
                            {doc.article && (
                              <span
                                className="px-2 py-0.5 text-xs font-medium bg-muted text-muted-foreground"
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
                              className="shrink-0 text-muted-foreground hover:text-foreground"
                              onClick={(e) => e.stopPropagation()}
                              aria-label={`Mở link ${doc.title}`}
                            >
                              <ExternalLink className="size-3.5" />
                            </motion.a>
                          )}
                        </div>

                        {/* Title */}
                        <h4 className="text-xs font-bold leading-snug mb-1.5" style={{ color: "var(--foreground)" }}>
                          {doc.title}
                        </h4>

                        {/* Excerpt */}
                        <p className="text-xs leading-relaxed line-clamp-2" style={{ color: "var(--muted-foreground)" }}>
                          {doc.excerpt}
                        </p>

                        {/* Date */}
                        {doc.date && (
                          <p className="text-xs mt-2 font-medium" style={{ color: "var(--foreground)", opacity: 0.8 }}>
                            {doc.date}
                          </p>
                        )}
                      </div>
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
