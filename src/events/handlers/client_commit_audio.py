"""Handler for inbound ``commit_audio`` messages from the browser.

Sends the OpenAI Realtime ``input_audio_buffer.commit`` client event.
Docs: https://platform.openai.com/docs/api-reference/realtime-client-events/input_audio_buffer/commit
"""

from __future__ import annotations

from typing import Any

from src.events.base import HandlerContext
from src.events.handlers import client_router


@client_router.register_for("commit_audio")
async def handle(message: dict[str, Any], ctx: HandlerContext) -> None:
    await ctx.manager.send_client_event(
        ctx.session_id, {"type": "input_audio_buffer.commit"}
    )
