"""Conector simples para OpenAI Chat Completions."""

import os
from typing import Any, Dict, List

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


def get_openai_client():
    """Retorna cliente OpenAI se houver API key configurada."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not OpenAI:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def generate_with_context(
    client: Any,
    model: str,
    pergunta: str,
    evidencia: str,
    max_tokens: int = 180,
) -> str:
    """Gera resposta usando evidência como base."""
    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "Você é um atendente de suporte de entregas. Responda em português, "
                "em até 2 frases curtas, usando apenas a evidência fornecida. "
                "Se faltar informação, peça dados adicionais."
            ),
        },
        {
            "role": "user",
            "content": f"Pergunta: {pergunta}\nEvidência: {evidencia}\nResposta:",
        },
    ]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0,
    )
    return completion.choices[0].message.content.strip()
