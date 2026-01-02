"""Utilitário para ler pedidos mock e buscar por order_id."""
import json
from pathlib import Path
from typing import Dict, Any

ORDERS_PATH = Path(__file__).resolve().parent.parent / "data" / "orders.json"


def _load_orders() -> Dict[str, Any]:
    with ORDERS_PATH.open("r", encoding="utf-8") as f:
        orders = json.load(f)
    return {o["order_id"]: o for o in orders}


ORDERS = _load_orders()


def get_order(order_id: str) -> Dict[str, Any] | None:
    """Retorna pedido pelo ID, se existir."""
    return ORDERS.get(order_id)
