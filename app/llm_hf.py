"""Conector simples para modelos da Hugging Face via transformers."""
import os
from functools import lru_cache
from typing import Optional, Any

from transformers import pipeline


@lru_cache(maxsize=1)
def get_hf_pipeline(model_name: Optional[str] = None) -> Any:
    """Retorna um pipeline de geração de texto; carrega sob demanda.

    - Define o modelo via env `HF_MODEL` ou parâmetro.
    - Usa task `text2text-generation` (modelos estilo T5/FLAN).
    - Requer dependências extras (torch) instaladas.
    """
    name = model_name or os.getenv("HF_MODEL", "google/flan-t5-small")
    return pipeline("text2text-generation", model=name)
 