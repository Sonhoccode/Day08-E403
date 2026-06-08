import type { Citation, Message } from "../components/ChatMessage";
import type { SourceDocument } from "../components/SourceDocuments";

export interface ChatTurn {
  role: Message["role"];
  content: string;
}

export interface ChatApiResponse {
  answer: string;
  citations: Citation[];
  sources: SourceDocument[];
  retrieval_source: string;
  memory_summary: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function sendChatMessage(
  message: string,
  messages: ChatTurn[],
  topK = 5,
): Promise<ChatApiResponse> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      messages,
      top_k: topK,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Chat API error (${response.status}): ${text}`);
  }

  return (await response.json()) as ChatApiResponse;
}
