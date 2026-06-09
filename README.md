

### Kiến Trúc Hệ Thống

```text
                         +----------------------+
                         |      Người dùng      |
                         +----------+-----------+
                                    |
                                    v
                    +---------------+----------------+
                    | Frontend React/Vite / Chainlit |
                    +---------------+----------------+
                                    |
                                    v
                         +----------+----------+
                         |   FastAPI /api/chat  |
                         +----------+----------+
                                    |
                                    v
                     +--------------+--------------+
                     | Memory summary + history     |
                     +--------------+--------------+
                                    |
                                    v
                     +--------------+--------------+
                     | generate_with_citation()     |
                     +--------------+--------------+
                                    |
                                    v
                     +--------------+--------------+
                     | classify_query()             |
                     +--------------+--------------+
                                    |
                                    v
                     +--------------+--------------+
                     | retrieve()                   |
                     +--------------+--------------+
                        |                        |
                        v                        v
              +---------+---------+    +---------+---------+
              | Semantic Search   |    | Lexical Search    |
              | (dense)           |    | (BM25/sparse)     |
              +---------+---------+    +---------+---------+
                        \                /
                         \              /
                          v            v
                        +--------------+--------------+
                        | Merge / RRF + Reranking     |
                        +--------------+--------------+
                                       |
                                       v
                              +--------+--------+
                              | Score đủ tốt?   |
                              +---+--------+----+
                                  |        |
                                 Có      Không
                                  |        |
                                  v        v
                         +--------+--+   +------------------+
                         |    LLM    |   | PageIndex fallback|
                         +--------+--+   +------------------+
                                  \        /
                                   \      /
                                    v    v
                           +--------+------+
                           | Answer + cite  |
                           +--------+------+
                                    |
                                    v
                         +----------+----------+
                         | Trả về cho frontend |
                         +----------------------+

Ingestion pipeline:

Task 1 Collect legal docs + Task 2 Crawl news
                    |
                    v
            Task 3 Convert markdown
                    |
                    v
           Task 4 Chunking + indexing
                    |
                    v
   Vector store / BM25 / PageIndex input

Evaluation:

Golden dataset -> Evaluation pipeline -> A/B comparison -> results.md
```

Kiến trúc tách thành 3 phần chính:

- `Ingestion`: thu thập, chuẩn hoá và index dữ liệu pháp luật + tin tức.
- `Runtime`: nhận câu hỏi, truy hồi ngữ cảnh, rerank, fallback và sinh câu trả lời có citation.
- `Eval`: dùng golden dataset để đo chất lượng và so sánh nhiều cấu hình.

---

### Phân Công Công Việc

| Thành viên | MSSV | Nhiệm vụ | Trạng thái |
|-----------|------|----------|------------|
| Hoàng Ích Cao Sơn |2A202600553 | Xây dựng backend | Hoàn thành |
| Hoàng Long Vũ |2A202600746 | Xây dựng giao diện | Hoàn thành |
| Nguyễn Thị Yến |2A202600645 | Xây dựng consevation memory | Hoàn thành |
| Nguyễn Quốc Tiến |2A202600551 | Xây dựng RAG pipeline | Hoàn thành |

 - Hoàng Ích Cao Sơn
2A202600746 - Hoàng Long Vũ
2A202600645 - Nguyễn Thị Yến
2A202600551 - Nguyễn Quốc Tiến
---

### Hướng Dẫn Chạy

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy app
streamlit run app.py
# hoặc
chainlit run app.py
```

---

### Lưu ý

Hãy giữ lại repo này nếu như bạn học track 3 giai đoạn 2, chúng ta sẽ phát triển tiếp dự án lên knowledge graph để khắc phục các câu hỏi hóc búa khi có các câu hỏi khó.

---

## Cài Đặt Môi Trường

```bash
pip install -r requirements.txt
```

Tạo file `.env` từ `.env.example`:
```bash
cp .env.example .env
# Điền API keys vào .env
```

---

## Chấm Điểm

### Tổng Quan Phân Bổ Điểm

| Thành phần | Tỷ trọng | Mô tả |
|-----------|----------|-------|
| **Bài Cá Nhân** | **50%** | 10 tasks, chấm bằng automated tests + manual review |
| **Bài Nhóm** | **30%** | RAG Chatbot + Evaluation pipeline |
| **Bonus** | **20%** | Các tiêu chí nâng cao (xem bên dưới) |

---

### Bài Cá Nhân — 50 điểm (50%)

Chấm bằng automated test suite (`pytest tests/ -v`). Mỗi task có test riêng.

| Task | Nội dung | Điểm | Test |
|------|----------|------|------|
| 1 | Thu thập văn bản pháp luật (≥3 files tồn tại trong `data/landing/legal/`) | 3 | `test_task1_*` |
| 2 | Crawl bài báo (≥5 files tồn tại trong `data/landing/news/`) | 3 | `test_task2_*` |
| 3 | Convert markdown (files tồn tại trong `data/standardized/`) | 4 | `test_task3_*` |
| 4 | Chunking + Indexing (vector store có data) | 7 | `test_task4_*` |
| 5 | Semantic search trả về kết quả đúng format, sorted | 6 | `test_task5_*` |
| 6 | Lexical search (BM25) trả về kết quả đúng format | 6 | `test_task6_*` |
| 7 | Reranking hoạt động, output re-sorted | 6 | `test_task7_*` |
| 8 | PageIndex query trả về kết quả | 4 | `test_task8_*` |
| 9 | Retrieval pipeline + fallback logic hoạt động | 7 | `test_task9_*` |
| 10 | Generation có citation + reorder | 4 | `test_task10_*` |
| **Tổng** | | **50** | |

---

### Bài Nhóm — 30 điểm (30%)

| Tiêu chí | Điểm |
|----------|------|
| RAG Chatbot demo hoạt động được | 8 |
| Tích hợp pipeline các thành viên | 4 |
| Kiến trúc rõ ràng + README | 3 |
| Chất lượng câu trả lời (có citation, đúng nội dung) | 3 |
| **Evaluation pipeline** (DeepEval / RAGAS / TruLens) | **12** |
| — Golden dataset ≥15 Q&A pairs | 3 |
| — Chạy eval với ≥4 metrics | 4 |
| — So sánh A/B ≥2 configs + phân tích | 3 |
| — Báo cáo kết quả có phân tích worst performers | 2 |

---

### Bonus — 20 điểm (20%)

Demo hoặc đặt câu hỏi mà nhóm đang demo khiến LLM không trả lời được (mỗi câu 5 điểm)

---

### Chạy Test Chấm Điểm Bài Cá Nhân

```bash
# Chạy toàn bộ test suite
pytest tests/ -v

# Chạy từng task
pytest tests/test_individual.py::TestTask1 -v
pytest tests/test_individual.py::TestTask5 -v
```

---

## Hướng Dẫn Thời Gian

| Giai đoạn | Thời gian | Hoạt động |
|-----------|-----------|-----------|
| Task 1–3 | 0:00–0:45 | Thu thập data + convert markdown |
| Task 4–6 | 0:45–1:45 | Chunking, indexing, search modules |
| Task 7–8 | 1:45–2:15 | Reranking + PageIndex setup |
| Task 9–10 | 2:15–3:00 | Pipeline hoàn chỉnh + generation |
| Bài nhóm | Ngoài giờ | Tích hợp + build demo |

---

## Tài Liệu Tham Khảo

- [Crawl4AI](https://github.com/unclecode/crawl4ai) — Web crawling library
- [MarkItDown](https://github.com/microsoft/markitdown) — Microsoft document converter
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/) — Chunking strategies
- [Weaviate](https://weaviate.io/developers/weaviate) — Vector database with hybrid search
- [rank-bm25](https://github.com/dorianbrown/rank_bm25) — BM25 implementation
- [PageIndex](https://github.com/VectifyAI/PageIndex) — Vectorless RAG
- [Jina Reranker](https://jina.ai/reranker/) — Cross-encoder reranking API
- Liu et al. (2023), *Lost in the Middle: How Language Models Use Long Contexts*
# Day08_RAG_pipeline_cohort2
