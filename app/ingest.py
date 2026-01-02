"""Script simples de ingestão para gerar índice vetorial (TF-IDF) a partir do KB."""

import json
from pathlib import Path
from typing import List, Dict, Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KB_PATH = DATA_DIR / "source" / "kb.json"
INDEX_PATH = DATA_DIR / "cache" / "kb_index.joblib"


def load_kb() -> List[Dict[str, Any]]:
    with KB_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_index(docs: List[Dict[str, Any]]) -> None:
    corpus = [f"{d['pergunta']} {d['resposta']}" for d in docs]
    vectorizer = TfidfVectorizer(stop_words=None)
    matrix = vectorizer.fit_transform(corpus)
    payload = {"docs": docs, "vectorizer": vectorizer, "matrix": matrix}
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, INDEX_PATH)
    print(f"Índice salvo em {INDEX_PATH}")


if __name__ == "__main__":
    kb_docs = load_kb()
    build_index(kb_docs)
