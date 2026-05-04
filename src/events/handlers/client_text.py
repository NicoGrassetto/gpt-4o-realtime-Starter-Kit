"""Handler for inbound ``text`` messages from the browser.

Sends a ``RealtimeUserInputMessage`` with an ``input_text`` part.
Docs: https://openai.github.io/openai-agents-python/ref/realtime/config/#agents.realtime.config.RealtimeUserInputMessage
"""

from __future__ import annotations

from typing import Any

from agents.realtime.config import RealtimeUserInputMessage

from src.events.base import HandlerContext
from src.events.handlers import client_router


@client_router.register_for("text")
async def handle(message: dict[str, Any], ctx: HandlerContext) -> None:
    text = message.get("text", "")
    if not text:
        return
    user_msg: RealtimeUserInputMessage = {
        "type": "message",
        "role": "user",
        "content": [
            {"type": "input_text", "text": text},
        ],
    }
    await ctx.manager.send_user_message(ctx.session_id, user_msg)
