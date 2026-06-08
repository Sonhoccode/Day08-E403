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

const gradients = [
  "linear-gradient(135deg, #4f46e5, #7c3aed)",
  "linear-gradient(135deg, #dc2626, #f97316)",
  "linear-gradient(135deg, #059669, #10b981)",
  "linear-gradient(135deg, #0891b2, #0ea5e9)",
  "linear-gradient(135deg, #7c3aed, #a78bfa)",
  "linear-gradient(135deg, #b45309, #f59e0b)",
];

const glowColors = [
  "rgba(79,70,229,0.3)",
  "rgba(220,38,38,0.3)",
  "rgba(5,150,105,0.3)",
  "rgba(8,145,178,0.3)",
  "rgba(124,58,237,0.3)",
  "rgba(180,83,9,0.3)",
];

export function SuggestedQuestions({ questions, onQuestionClick }: SuggestedQuestionsProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 px-1">
        <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
        <span className="text-xs font-medium px-3 py-1 rounded-full"
          style={{
            color: "var(--muted-foreground)",
            background: "var(--muted)",
          }}
        >
          Câu hỏi gợi ý
        </span>
        <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {questions.map((question, index) => {
          const Icon = questionIcons[index % questionIcons.length];
          const gradient = gradients[index % gradients.length];
          const glow = glowColors[index % glowColors.length];

          return (
            <motion.button
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.07, duration: 0.35 }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onQuestionClick(question)}
              className="flex items-center gap-3 text-left p-3 rounded-xl group transition-all"
              style={{
                background: "var(--card)",
                border: "1px solid var(--border)",
                boxShadow: "0 2px 10px rgba(0,0,0,0.04)",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.boxShadow = `0 4px 20px ${glow}`;
                (e.currentTarget as HTMLElement).style.borderColor = `${glow.replace("0.3", "0.4")}`;
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.boxShadow = "0 2px 10px rgba(0,0,0,0.04)";
                (e.currentTarget as HTMLElement).style.borderColor = "var(--border)";
              }}
            >
              {/* Icon */}
              <div
                className="shrink-0 size-9 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110"
                style={{
                  background: gradient,
                  boxShadow: `0 3px 10px ${glow}`,
                }}
              >
                <Icon className="size-4 text-white" />
              </div>

              {/* Text */}
              <span
                className="flex-1 text-xs leading-snug"
                style={{ color: "var(--foreground)" }}
              >
                {question}
              </span>

              {/* Arrow */}
              <ChevronRight
                className="size-3.5 shrink-0 transition-transform group-hover:translate-x-0.5"
                style={{ color: "var(--muted-foreground)", opacity: 0.5 }}
              />
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
