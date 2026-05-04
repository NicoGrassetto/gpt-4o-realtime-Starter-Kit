"""Handler for ``tool_approval_required`` events.

Docs: https://openai.github.io/openai-agents-python/ref/realtime/events/#agents.realtime.events.RealtimeToolApprovalRequired
"""

from __future__ import annotations

from typing import Any

from agents.realtime import RealtimeSessionEvent

from src.events.base import HandlerContext
from src.events.handlers import server_router


@server_router.register_for("tool_approval_required")
async def handle(event: RealtimeSessionEvent, ctx: HandlerContext) -> dict[str, Any]:
    return {
        "type": "tool_approval_required",
        "tool": event.tool.name,
        "call_id": event.call_id,
        "arguments": event.arguments,
        "agent": event.agent.name,
    }
