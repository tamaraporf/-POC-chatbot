"""Roteador simples de intenções para o chat."""

from typing import Literal

Intent = Literal["pedido", "politica", "usuario", "faq"]


def detect_intent(message: str) -> Intent:
    text = message.lower()
    if "ped-" in text or "pedido" in text or "status" in text:
        return "pedido"
    if (
        "política" in text
        or "politica" in text
        or "reembolso" in text
        or "atraso" in text
    ):
        return "politica"
    if "user" in text or "usr-" in text or "cliente" in text:
        return "usuario"
    return "faq"
