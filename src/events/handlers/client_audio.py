"""Handler for inbound ``audio`` messages from the browser.

Forwards PCM16 audio to the realtime session via ``RealtimeSession.send_audio``.
Docs: https://openai.github.io/openai-agents-python/ref/realtime/session/#agents.realtime.session.RealtimeSession.send_audio
"""

from __future__ import annotations

import struct
from typing import Any

from src.events.base import HandlerContext
from src.events.handlers import client_router

# Max audio samples per WebSocket message (~20 s at 24 kHz mono 16-bit)
_MAX_AUDIO_SAMPLES = 960_000


@client_router.register_for("audio")
async def handle(message: dict[str, Any], ctx: HandlerContext) -> None:
    int16_data = message.get("data", [])
    if not isinstance(int16_data, list) or len(int16_data) > _MAX_AUDIO_SAMPLES:
        ctx.logger.warning(
            "Audio payload too large or invalid from session %s", ctx.session_id
        )
        return
    audio_bytes = struct.pack(f"{len(int16_data)}h", *int16_data)
    await ctx.manager.send_audio(ctx.session_id, audio_bytes)
