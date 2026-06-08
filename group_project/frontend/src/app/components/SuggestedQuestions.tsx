import { motion } from "motion/react";
import {
  Scale,
  Gavel,
  Newspaper,
  HeartPulse,
  FlaskConical,
  Shield,
  ChevronRight,
} from "lucide-react";

interface SuggestedQuestionsProps {
  questions: string[];
  onQuestionClick: (question: string) => void;
}

const questionIcons = [Scale, Gavel, Newspaper, HeartPulse, FlaskConical, Shield];

export function SuggestedQuestions({ questions, onQuestionClick }: SuggestedQuestionsProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-border" />
        <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Câu hỏi gợi ý
        </span>
        <div className="flex-1 h-px bg-border" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {questions.map((question, index) => {
          const Icon = questionIcons[index % questionIcons.length];

          return (
            <motion.button
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.07, duration: 0.35 }}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => onQuestionClick(question)}
              className="flex items-center gap-3 text-left p-3 border transition-colors group"
              style={{
                background: "var(--card)",
                borderColor: "var(--border)",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "var(--foreground)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "var(--border)";
              }}
            >
              {/* Icon */}
              <div
                className="shrink-0 size-10 flex items-center justify-center border transition-colors"
                style={{
                  background: "var(--muted)",
                  borderColor: "var(--border)",
                }}
              >
                <Icon className="size-4" style={{ color: "var(--foreground)" }} />
              </div>

              {/* Text */}
              <span
                className="flex-1 text-sm font-medium leading-snug"
                style={{ color: "var(--foreground)" }}
              >
                {question}
              </span>

              {/* Arrow */}
              <ChevronRight
                className="size-4 shrink-0 transition-transform group-hover:translate-x-1"
                style={{ color: "var(--muted-foreground)" }}
              />
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
