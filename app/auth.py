"""Autenticação simples via header X-API-Key."""
import os
from fastapi import Header, HTTPException, status


API_KEY = os.getenv("API_KEY")


def verify_api_key(x_api_key: str = Header(default=None)) -> None:
    """Valida API key se configurada; se não houver, permite acesso."""
    if API_KEY is None:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
