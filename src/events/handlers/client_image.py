"""Handler for inbound ``image`` messages from the browser.

Sends a ``RealtimeUserInputMessage`` containing an ``input_image`` part.
Docs: https://openai.github.io/openai-agents-python/ref/realtime/config/#agents.realtime.config.RealtimeUserInputMessage
"""

from __future__ import annotations

from typing import Any

from agents.realtime.config import RealtimeUserInputMessage

from src.events.base import HandlerContext
from src.events.handlers import client_router


@client_router.register_for("image")
async def handle(message: dict[str, Any], ctx: HandlerContext) -> None:
    data_url = message.get("data_url")
    if not data_url:
        return
    prompt_text = message.get("text") or "Please describe this image."
    user_msg: RealtimeUserInputMessage = {
        "type": "message",
        "role": "user",
        "content": [
            {"type": "input_image", "image_url": data_url, "detail": "high"},
            {"type": "input_text", "text": prompt_text},
        ],
    }
    await ctx.manager.send_user_message(ctx.session_id, user_msg)
