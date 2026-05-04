"""Handler for ``guardrail_tripped`` events.

Docs: https://openai.github.io/openai-agents-python/ref/realtime/events/#agents.realtime.events.RealtimeGuardrailTripped
"""

from __future__ import annotations

from typing import Any

from agents.realtime import RealtimeSessionEvent

from src.events.base import HandlerContext
from src.events.handlers import server_router


@server_router.register_for("guardrail_tripped")
async def handle(event: RealtimeSessionEvent, ctx: HandlerContext) -> dict[str, Any]:
    return {
        "type": "guardrail_tripped",
        "guardrail_results": [
            {"name": r.guardrail.name} for r in event.guardrail_results
        ],
    }
