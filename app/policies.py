"""Utilitário para políticas mockadas."""

import json
from pathlib import Path
from typing import Any, Dict

POLICIES_PATH = Path(__file__).resolve().parent.parent / "data" / "policies.json"


def load_policies() -> Dict[str, Any]:
    with POLICIES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


POLICIES = load_policies()


def get_policy(topic: str) -> Dict[str, Any] | None:
    topic_norm = topic.lower()
    for key, value in POLICIES.items():
        if key.lower() == topic_norm:
            return value
    return None
