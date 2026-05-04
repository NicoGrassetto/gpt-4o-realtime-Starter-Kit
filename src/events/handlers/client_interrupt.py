"""Handler for inbound ``interrupt`` messages from the browser.

Invokes ``RealtimeSession.interrupt`` to cancel any in-progress model response.
Docs: https://openai.github.io/openai-agents-python/ref/realtime/session/#agents.realtime.session.RealtimeSession.interrupt
"""

from __future__ import annotations

from typing import Any

from src.events.base import HandlerContext
from src.events.handlers import client_router


@client_router.register_for("interrupt")
async def handle(message: dict[str, Any], ctx: HandlerContext) -> None:
    await ctx.manager.interrupt(ctx.session_id)
