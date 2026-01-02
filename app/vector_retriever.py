"""Retriever baseado em índice TF-IDF salvo em disco."""

from pathlib import Path
from typing import List, Dict, Any

import joblib
from sklearn.metrics.pairwise import cosine_similarity


class VectorRetriever:
    def __init__(self, index_path: str | Path, top_k: int = 3) -> None:
        self.index_path = Path(index_path)
        payload = joblib.load(self.index_path)
        self.docs: List[Dict[str, Any]] = payload["docs"]
        self.vectorizer = payload["vectorizer"]
        self.matrix = payload["matrix"]
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        if not query.strip():
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        ranked = sorted(zip(self.docs, scores), key=lambda x: x[1], reverse=True)[
            : self.top_k
        ]
        results = []
        for doc, score in ranked:
            entry = doc.copy()
            entry["score"] = float(score)
            results.append(entry)
        return results
