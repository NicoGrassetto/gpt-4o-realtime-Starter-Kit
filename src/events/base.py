"""Shared types for event handlers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Protocol

from agents.realtime import RealtimeSessionEvent

if TYPE_CHECKING:
    from fastapi import WebSocket


@dataclass
class HandlerContext:
    """Context passed to every event handler."""

    session_id: str
    manager: Any  # SessionManager (avoid circular import)
    websocket: "WebSocket"
    logger: logging.Logger


class ServerEventHandler(Protocol):
    """Handler for an SDK ``RealtimeSessionEvent``.

    Returns the JSON-serializable payload to forward to the client, or
    ``None`` to suppress forwarding.
    """

    async def __call__(
        self, event: RealtimeSessionEvent, ctx: HandlerContext
    ) -> dict[str, Any] | None: ...


class ClientEventHandler(Protocol):
    """Handler for a parsed inbound browser WebSocket message."""

    async def __call__(
        self, message: dict[str, Any], ctx: HandlerContext
    ) -> None: ...


ServerHandlerFn = Callable[
    [RealtimeSessionEvent, HandlerContext], Awaitable[dict[str, Any] | None]
]
ClientHandlerFn = Callable[[dict[str, Any], HandlerContext], Awaitable[None]]
