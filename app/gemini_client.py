"""Conector simples para Gemini (Google Generative AI)."""

import os
from typing import Optional

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None  # type: ignore


def get_gemini_model(model_name: Optional[str] = None):
    """Retorna um modelo Gemini configurado se houver API key."""
    if not genai:
        return None
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(name)
    except Exception:
        return None


def generate_with_context(
    model, pergunta: str, evidencia: str, max_output_tokens: int = 180
) -> str:
    """Gera resposta usando evidência como base."""
    prompt = (
        "Você é um atendente de suporte de entregas. Responda em português, em até 2 frases curtas, "
        "usando apenas a evidência fornecida. Se faltar informação, peça dados adicionais.\n\n"
        f"Pergunta: {pergunta}\n"
        f"Evidência: {evidencia}\n"
        "Resposta:"
    )
    resp = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": max_output_tokens, "temperature": 0},
    )
    return resp.text.strip()
