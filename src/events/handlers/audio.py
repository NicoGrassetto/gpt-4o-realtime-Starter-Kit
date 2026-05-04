"""Handler for ``audio`` events (PCM chunks → base64).

Docs: https://openai.github.io/openai-agents-python/ref/realtime/events/#agents.realtime.events.RealtimeAudio
"""

from __future__ import annotations

import base64
from typing import Any

from agents.realtime import RealtimeSessionEvent

from src.events.base import HandlerContext
from src.events.handlers import server_router


@server_router.register_for("audio")
async def handle(event: RealtimeSessionEvent, ctx: HandlerContext) -> dict[str, Any]:
    return {
        "type": "audio",
        "audio": base64.b64encode(event.audio.data).decode("utf-8"),
    }
