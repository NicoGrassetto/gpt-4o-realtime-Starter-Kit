"""Handler registry.

Importing this module instantiates the singleton routers and imports each
handler module so its ``@router.register_for(...)`` decorator runs.
"""

from src.events.client_router import ClientEventRouter
from src.events.server_router import ServerEventRouter

# Singleton routers — handler modules import these to register themselves.
server_router = ServerEventRouter()
client_router = ClientEventRouter()

# Import handler modules to register them. Order doesn't matter; imports are
# kept after the router instantiation above to avoid a circular import.
from src.events.handlers import (  # noqa: E402, F401
    agent_end,
    agent_start,
    audio,
    audio_end,
    audio_interrupted,
    client_audio,
    client_commit_audio,
    client_image,
    client_interrupt,
    client_text,
    error,
    guardrail_tripped,
    handoff,
    history_added,
    history_updated,
    input_audio_timeout_triggered,
    raw_model_event,
    tool_approval_required,
    tool_end,
    tool_start,
)

__all__ = ["server_router", "client_router"]
