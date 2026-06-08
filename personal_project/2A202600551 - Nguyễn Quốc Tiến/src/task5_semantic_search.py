"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

db_path = Path(__file__).parent.parent / "data" / "chroma_db"
client = chromadb.PersistentClient(path=str(db_path))
try:
    collection = client.get_collection("DrugLawDocs")
except:
    collection = None
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    if not collection:
        print("Warning: ChromaDB collection not found.")
        return []

    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    output = []
    if not results["ids"] or not results["ids"][0]:
        return output
        
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        output.append({
            "content": doc,
            "score": 1.0 - float(dist), # cosine distance -> similarity
            "metadata": meta
        })
    return output


if __name__ == "__main__":
    # Test
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
