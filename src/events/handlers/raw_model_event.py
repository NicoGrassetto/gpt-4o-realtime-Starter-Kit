"""Handler for ``raw_model_event`` events.

Docs: https://openai.github.io/openai-agents-python/ref/realtime/events/#agents.realtime.events.RealtimeRawModelEvent
"""

from __future__ import annotations

from typing import Any

from agents.realtime import RealtimeSessionEvent

from src.events.base import HandlerContext
from src.events.handlers import server_router


@server_router.register_for("raw_model_event")
async def handle(event: RealtimeSessionEvent, ctx: HandlerContext) -> dict[str, Any]:
    return {
        "type": "raw_model_event",
        "raw_model_event": {"type": event.data.type},
    }
