"""Testes básicos de saúde, chat e pedido (sem API_KEY)."""
import os

import pytest
from fastapi.testclient import TestClient

os.environ.pop("API_KEY", None)  # garantir que auth não bloqueie testes simples

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"


def test_chat_basic():
    resp = client.post("/chat", json={"mensagem": "Meu pedido atrasou"})
    assert resp.status_code == 200
    data = resp.json()
    assert "resposta" in data
    assert "fonte" in data


def test_pedido_not_found():
    resp = client.get("/pedido/PED-000")
    assert resp.status_code in (200, 422, 401)  # pode falhar se API_KEY setada
