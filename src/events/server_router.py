"""Router for outbound SDK events (server → client)."""

from __future__ import annotations

from typing import Any

from agents.realtime import RealtimeSessionEvent

from src.events.base import HandlerContext, ServerHandlerFn


class ServerEventRouter:
    """Dispatches ``RealtimeSessionEvent`` instances to per-type handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ServerHandlerFn] = {}

    def register(self, event_type: str, handler: ServerHandlerFn) -> None:
        if event_type in self._handlers:
            raise ValueError(f"Handler for '{event_type}' already registered")
        self._handlers[event_type] = handler

    def register_for(self, event_type: str):
        def decorator(fn: ServerHandlerFn) -> ServerHandlerFn:
            self.register(event_type, fn)
            return fn

        return decorator

    async def dispatch(
        self, event: RealtimeSessionEvent, ctx: HandlerContext
    ) -> dict[str, Any] | None:
        handler = self._handlers.get(event.type)
        if handler is None:
            ctx.logger.warning(
                "No handler registered for server event type '%s'", event.type
            )
            return {"type": event.type}
        return await handler(event, ctx)

    @property
    def registered_types(self) -> list[str]:
        return sorted(self._handlers.keys())
