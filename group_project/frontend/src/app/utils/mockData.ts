import { Citation, Message } from "../components/ChatMessage";
import { SourceDocument } from "../components/SourceDocuments";

export interface ConversationTurn {
  role: Message["role"];
  content: string;
}

export interface ConversationMemory {
  turns: ConversationTurn[];
  topic?: string;
  lastUserQuestion?: string;
  summary: string;
}

// Mock data cho các câu trả lời và tài liệu nguồn
export const mockResponses: Record<
  string,
  {
    answer: string;
    citations: Citation[];
    sources: SourceDocument[];
  }
> = {
  default: {
    answer:
      "Theo quy định tại Luật Phòng, chống ma túy 2021, các hành vi liên quan đến ma túy đều bị nghiêm cấm và xử phạt nghiêm khắc. Tùy vào tính chất và mức độ vi phạm, người vi phạm có thể bị xử phạt hành chính hoặc truy cứu tr책nhiệm hình sự.\n\nCác hành vi bị nghiêm cấm bao gồm: trồng cây có chứa chất ma túy, sản xuất, mua bán, vận chuyển, tàng trữ, sử dụng trái phép chất ma túy.",
    citations: [
      {
        id: "c1",
        text: "Luật Phòng, chống ma túy 2021",
        source: "Luật số 66/2021/QH14",
        article: "Điều 5",
      },
      {
        id: "c2",
        text: "Các hành vi bị nghiêm cấm",
        source: "Luật số 66/2021/QH14",
        article: "Điều 8",
      },
    ],
    sources: [
      {
        id: "s1",
        title: "Luật Phòng, chống ma túy năm 2021",
        type: "law",
        article: "Điều 5, Điều 8",
        excerpt:
          "Nhà nước có chính sách phòng ngừa, ngăn chặn, đấu tranh chống tội phạm và tệ nạn ma túy; quản lý người nghiện ma túy, người sử dụng trái phép chất ma túy; cai nghiện ma túy, quản lý sau cai nghiện ma túy...",
        url: "#",
        date: "Có hiệu lực từ 01/01/2022",
      },
      {
        id: "s2",
        title: "Bộ luật Hình sự 2015 (sửa đổi, bổ sung 2017)",
        type: "law",
        article: "Điều 249-259",
        excerpt:
          "Quy định các tội phạm về ma túy bao gồm: tội tổ chức, ép buộc người khác sử dụng trái phép chất ma túy, tội tàng trữ, vận chuyển, mua bán trái phép chất ma túy...",
        url: "#",
        date: "Có hiệu lực từ 01/01/2018",
      },
    ],
  },
  mức_phạt: {
    answer:
      "Mức phạt đối với các hành vi liên quan đến ma túy được quy định rất nghiêm khắc:\n\n1. **Xử phạt hành chính**: Đối với hành vi tàng trữ, sử dụng trái phép chất ma túy ở mức độ nhẹ, phạt tiền từ 500.000đ đến 100.000.000đ, có thể kèm theo các biện pháp giáo dục tại xã, phường, thị trấn hoặc đưa vào cơ sở cai nghiện bắt buộc.\n\n2. **Truy cứu trách nhiệm hình sự**: \n- Tội tàng trữ trái phép chất ma túy: Phạt tù từ 6 tháng đến 20 năm hoặc tù chung thân, tùy thuộc vào số lượng và loại chất ma túy.\n- Tội mua bán trái phép chất ma túy: Phạt tù từ 2 năm đến 20 năm, tù chung thân hoặc tử hình.\n- Tội tổ chức sử dụng trái phép chất ma túy: Phạt tù từ 2 năm đến 7 năm.",
    citations: [
      {
        id: "c3",
        text: "Nghị định 167/2013/NĐ-CP",
        source: "Nghị định 167/2013/NĐ-CP",
        article: "Điều 14, 15, 16",
      },
      {
        id: "c4",
        text: "Bộ luật Hình sự 2015",
        source: "Bộ luật Hình sự",
        article: "Điều 249-259",
      },
    ],
    sources: [
      {
        id: "s3",
        title: "Nghị định 167/2013/NĐ-CP về xử phạt vi phạm hành chính",
        type: "regulation",
        article: "Điều 14, 15, 16",
        excerpt:
          "Quy định xử phạt hành chính trong lĩnh vực phòng, chống ma túy, mại dâm. Mức phạt tiền đối với hành vi tàng trữ trái phép chất ma túy từ 500.000đ đến 50.000.000đ...",
        url: "#",
        date: "Ban hành ngày 12/11/2013",
      },
      {
        id: "s4",
        title: "Bộ luật Hình sự 2015 - Chương XIII: Tội phạm về ma túy",
        type: "law",
        article: "Điều 249-259",
        excerpt:
          "Người nào tổ chức, cưỡng ép, lôi kéo, dụ dỗ, kích động người khác sử dụng trái phép chất ma túy thì bị phạt tù từ 02 năm đến 07 năm...",
        url: "#",
        date: "Có hiệu lực từ 01/01/2018",
      },
    ],
  },
  tin_tức: {
    answer:
      "Gần đây, lực lượng chức năng đã triệt phá nhiều vụ án ma túy lớn:\n\n1. **Vụ án tại TP.HCM** (tháng 5/2026): Bắt giữ đường dây vận chuyển hơn 300kg ma túy từ Campuchia vào Việt Nam. Đây là một trong những vụ án lớn nhất năm với số lượng tang vật khủng.\n\n2. **Chuyên án tại biên giới** (tháng 4/2026): Phát hiện và triệt phá đường dây sản xuất ma túy tổng hợp tại khu vực biên giới, thu giữ hàng ngàn viên ma túy tổng hợp và nhiều dụng cụ sản xuất.\n\n3. **Tình hình chung**: Tội phạm ma túy vẫn diễn biến phức tạp, đặc biệt là ma túy tổng hợp. Các đối tượng ngày càng tinh vi trong thủ đoạn vận chuyển và che giấu.",
    citations: [
      {
        id: "c5",
        text: "Báo Công an nhân dân",
        source: "Báo CAND - 15/05/2026",
      },
      {
        id: "c6",
        text: "Báo Thanh niên",
        source: "Báo Thanh niên - 22/04/2026",
      },
    ],
    sources: [
      {
        id: "s5",
        title: "Triệt phá đường dây vận chuyển 300kg ma túy từ Campuchia",
        type: "news",
        excerpt:
          "Công an TP.HCM phối hợp với các đơn vị nghiệp vụ Bộ Công an đã triệt phá thành công đường dây vận chuyển ma túy xuyên quốc gia, bắt giữ 15 đối tượng, thu giữ hơn 300kg các loại ma túy...",
        url: "#",
        date: "15/05/2026",
      },
      {
        id: "s6",
        title: "Phá xưởng sản xuất ma túy tổng hợp tại biên giới",
        type: "news",
        excerpt:
          "Lực lượng Biên phòng phối hợp với Công an tỉnh đã ập vào triệt phá xưởng sản xuất ma túy tổng hợp hoạt động ngụy trang tinh vi, thu giữ hàng chục ngàn viên ma túy cùng nhiều hóa chất độc hại...",
        url: "#",
        date: "22/04/2026",
      },
    ],
  },
};

export const suggestedQuestions = [
  "Các hành vi liên quan đến ma túy bị nghiêm cấm là gì?",
  "Mức phạt đối với tội tàng trữ ma túy là bao nhiêu?",
  "Tin tức mới nhất về tình hình ma túy tại Việt Nam?",
  "Quy định về cai nghiện ma túy bắt buộc?",
  "Sự khác biệt giữa ma túy tự nhiên và ma túy tổng hợp?",
  "Các biện pháp phòng chống ma túy của Nhà nước?",
];

function detectTopic(text: string): string | undefined {
  const message = text.toLowerCase();

  if (
    message.includes("mức phạt") ||
    message.includes("xử phạt") ||
    message.includes("phạt tù") ||
    message.includes("điều 249") ||
    message.includes("điều 251")
  ) {
    return "criminal_penalties";
  }

  if (
    message.includes("cai nghiện") ||
    message.includes("phòng chống ma túy") ||
    message.includes("phòng, chống ma túy") ||
    message.includes("nghiện ma túy")
  ) {
    return "prevention_and_treatment";
  }

  if (
    message.includes("tin tức") ||
    message.includes("mới nhất") ||
    message.includes("gần đây") ||
    message.includes("báo") ||
    message.includes("vụ án")
  ) {
    return "news";
  }

  return undefined;
}

function isFollowUpQuestion(text: string) {
  const message = text.toLowerCase().trim();
  return (
    message.length < 45 ||
    /(còn|thế còn|vậy|đó|nó|chi tiết|giải thích thêm|tiếp theo|nữa|trong trường hợp đó|về vấn đề này)/.test(message)
  );
}

function getMemoryTopic(memory?: ConversationMemory) {
  return memory?.topic || memory?.summary || "general";
}

export function summarizeConversation(memory: ConversationTurn[]): string {
  if (memory.length === 0) {
    return "Chưa có lịch sử hội thoại.";
  }

  const recent = memory.slice(-6);
  const userQuestions = recent.filter((turn) => turn.role === "user").map((turn) => turn.content);
  const lastQuestion = userQuestions.at(-1) || "";
  const topic = detectTopic(lastQuestion);

  if (topic === "criminal_penalties") {
    return "Đang trao đổi về mức phạt và trách nhiệm hình sự liên quan đến ma túy.";
  }

  if (topic === "prevention_and_treatment") {
    return "Đang trao đổi về phòng, chống ma túy và cai nghiện.";
  }

  if (topic === "news") {
    return "Đang trao đổi về tin tức, vụ án và tình hình ma túy gần đây.";
  }

  return `Đang theo dõi ${userQuestions.length} câu hỏi gần nhất, chủ đề hiện tại là: ${lastQuestion || "chưa xác định"}.`;
}

function pickResponseByTopic(topic?: string) {
  if (topic === "criminal_penalties") return mockResponses.mức_phạt;
  if (topic === "prevention_and_treatment") return mockResponses.default;
  if (topic === "news") return mockResponses.tin_tức;
  return mockResponses.default;
}

export function generateMockResponse(
  userMessage: string,
  memory?: ConversationMemory
): {
  answer: string;
  citations: Citation[];
  sources: SourceDocument[];
} {
  const message = userMessage.toLowerCase();
  const topicFromMessage = detectTopic(message);
  const topicFromMemory = memory?.topic;
  const followUp = isFollowUpQuestion(message);

  if (followUp && topicFromMemory && !topicFromMessage) {
    return pickResponseByTopic(topicFromMemory);
  }

  if (message.includes("mức phạt") || message.includes("xử phạt") || message.includes("phạt tù")) {
    return mockResponses.mức_phạt;
  }

  if (message.includes("tin tức") || message.includes("mới nhất") || message.includes("gần đây")) {
    return mockResponses.tin_tức;
  }

  return mockResponses.default;
}

// Hàm mô phỏng API call với delay
export async function simulateAPICall(
  userMessage: string,
  memory?: ConversationMemory
): Promise<Message> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1500 + Math.random() * 1000));

  const response = generateMockResponse(userMessage, memory);

  return {
    id: Date.now().toString(),
    role: "assistant",
    content: response.answer,
    citations: response.citations,
    timestamp: new Date(),
  };
}

export function buildConversationMemory(messages: Message[]): ConversationMemory {
  const turns: ConversationTurn[] = messages.slice(-6).map((message) => ({
    role: message.role,
    content: message.content,
  }));

  const lastUserQuestion = [...messages].reverse().find((message) => message.role === "user")?.content;
  const topic = lastUserQuestion ? detectTopic(lastUserQuestion) : undefined;

  return {
    turns,
    topic,
    lastUserQuestion,
    summary: summarizeConversation(turns),
  };
}
