"""
Phase 2 - Step 2: Lightweight RAG retrieval over the knowledge base.

Uses TF-IDF + cosine similarity instead of a heavier embedding model. For a
knowledge base this small (a handful of short documents), TF-IDF retrieval
is fast, dependency-light, needs no API key, and is good enough to ground
the investigator agent. Swap in a proper embedding model later if you want
semantic (not just keyword) retrieval.
"""

import glob
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KNOWLEDGE_BASE_DIR = "knowledge_base"


class KnowledgeBase:
    def __init__(self, kb_dir: str = KNOWLEDGE_BASE_DIR):
        self.doc_names = []
        self.doc_texts = []
        for path in sorted(glob.glob(os.path.join(kb_dir, "*.txt"))):
            with open(path) as f:
                text = f.read()
            self.doc_names.append(os.path.basename(path))
            self.doc_texts.append(text)

        if not self.doc_texts:
            raise ValueError(
                f"No .txt files found in '{kb_dir}'. "
                "Add knowledge base documents before running Phase 2."
            )

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform(self.doc_texts)

    def retrieve(self, query: str, top_k: int = 3) -> list:
        """Return the top_k most relevant documents for a query string."""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.doc_matrix)[0]
        ranked = sorted(
            zip(self.doc_names, self.doc_texts, scores),
            key=lambda x: x[2],
            reverse=True,
        )
        return [
            {"source": name, "text": text, "score": round(float(score), 4)}
            for name, text, score in ranked[:top_k]
            if score > 0
        ]


if __name__ == "__main__":
    kb = KnowledgeBase()
    print(f"[rag] Indexed {len(kb.doc_names)} documents: {kb.doc_names}")
    test_query = "close approach high relative velocity should we maneuver"
    results = kb.retrieve(test_query, top_k=3)
    print(f"\n[rag] Test query: '{test_query}'")
    for r in results:
        print(f"  {r['source']}  (score={r['score']})")