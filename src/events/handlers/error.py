"""Handler for ``error`` events.

Docs: https://openai.github.io/openai-agents-python/ref/realtime/events/#agents.realtime.events.RealtimeError
"""

from __future__ import annotations

from typing import Any

from agents.realtime import RealtimeSessionEvent

from src.events.base import HandlerContext
from src.events.handlers import server_router


@server_router.register_for("error")
async def handle(event: RealtimeSessionEvent, ctx: HandlerContext) -> dict[str, Any]:
    error = str(event.error) if hasattr(event, "error") else "Unknown"
    return {"type": "error", "error": error}
