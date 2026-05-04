"""Handler for ``history_updated`` events.

Docs: https://openai.github.io/openai-agents-python/ref/realtime/events/#agents.realtime.events.RealtimeHistoryUpdated
"""

from __future__ import annotations

from typing import Any

from agents.realtime import RealtimeSessionEvent

from src.events.base import HandlerContext
from src.events.handlers import server_router
from src.events.handlers._history import sanitize_history_item


@server_router.register_for("history_updated")
async def handle(event: RealtimeSessionEvent, ctx: HandlerContext) -> dict[str, Any]:
    return {
        "type": "history_updated",
        "history": [sanitize_history_item(item) for item in event.history],
    }
