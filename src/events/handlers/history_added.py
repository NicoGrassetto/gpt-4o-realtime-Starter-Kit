"""Handler for ``history_added`` events.

Docs: https://openai.github.io/openai-agents-python/ref/realtime/events/#agents.realtime.events.RealtimeHistoryAdded
"""

from __future__ import annotations

from typing import Any

from agents.realtime import RealtimeSessionEvent

from src.events.base import HandlerContext
from src.events.handlers import server_router
from src.events.handlers._history import sanitize_history_item


@server_router.register_for("history_added")
async def handle(event: RealtimeSessionEvent, ctx: HandlerContext) -> dict[str, Any]:
    try:
        item = sanitize_history_item(event.item)
    except Exception:  # noqa: BLE001 — match prior defensive behaviour
        item = None
    return {"type": "history_added", "item": item}
