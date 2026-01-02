"""Utilitário para usuários mockados."""
import json
from pathlib import Path
from typing import Any, Dict

USERS_PATH = Path(__file__).resolve().parent.parent / "data" / "users.json"


def load_users() -> Dict[str, Any]:
    with USERS_PATH.open("r", encoding="utf-8") as f:
        users = json.load(f)
    return {u["user_id"].lower(): u for u in users}


USERS = load_users()


def get_user(user_id: str) -> Dict[str, Any] | None:
    return USERS.get(user_id.lower())
