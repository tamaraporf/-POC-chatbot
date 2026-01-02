import json
from pathlib import Path
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeBaseRetriever:
    """Carrega o KB de FAQ/políticas e faz busca por similaridade."""

    def __init__(self, kb_path: str | Path, top_k: int = 3) -> None:
        self.kb_path = Path(kb_path)
        self.top_k = top_k
        self._docs: List[Dict[str, Any]] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._load()

        # NOTA: Para trocar TF-IDF por embeddings + índice vetorial:
        # - Use embeddings (local ex.: sentence-transformers) ou API (OpenAI).
        # - Índice local: FAISS (IndexFlatIP para similaridade). Passos:
        #     1) gerar embedding de cada doc e empilhar em uma matriz numpy;
        #     2) index = faiss.IndexFlatIP(dim); index.add(matrix);
        #     3) no retrieve: embedding da query -> index.search(query_vec, top_k).
        # - Índice em banco: Postgres + pgvector. Passos:
        #     1) criar tabela com coluna vector(d);
        #     2) inserir docs com embeddings já calculados;
        #     3) query SQL: ORDER BY embedding <=> :query_embedding LIMIT k.

    def _load(self) -> None:
        """Carrega documentos do JSON e monta a matriz TF-IDF."""
        with self.kb_path.open("r", encoding="utf-8") as f:
            self._docs = json.load(f)
        corpus = [f"{d['pergunta']} {d['resposta']}" for d in self._docs]
        # Nota: sklearn não tem stopwords nativas em português; usando None para simplicidade.
        self._vectorizer = TfidfVectorizer(stop_words=None)
        self._matrix = self._vectorizer.fit_transform(corpus)

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retorna top-k entradas do KB ranqueadas por similaridade cosseno."""
        if not query.strip():
            return []
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
        ranked = sorted(zip(self._docs, scores), key=lambda x: x[1], reverse=True)[
            : self.top_k
        ]
        results = []
        for doc, score in ranked:
            entry = doc.copy()
            entry["score"] = float(score)
            results.append(entry)
        return results
