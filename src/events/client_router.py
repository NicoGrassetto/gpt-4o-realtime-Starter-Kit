"""Router for inbound browser messages (client → server)."""

from __future__ import annotations

from typing import Any

from src.events.base import ClientHandlerFn, HandlerContext


class ClientEventRouter:
    """Dispatches parsed browser WebSocket messages to per-type handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ClientHandlerFn] = {}

    def register(self, message_type: str, handler: ClientHandlerFn) -> None:
        if message_type in self._handlers:
            raise ValueError(f"Handler for '{message_type}' already registered")
        self._handlers[message_type] = handler

    def register_for(self, message_type: str):
        def decorator(fn: ClientHandlerFn) -> ClientHandlerFn:
            self.register(message_type, fn)
            return fn

        return decorator

    async def dispatch(self, message: dict[str, Any], ctx: HandlerContext) -> None:
        msg_type = message.get("type")
        if not msg_type:
            ctx.logger.warning(
                "Client message missing 'type' from session %s", ctx.session_id
            )
            return
        handler = self._handlers.get(msg_type)
        if handler is None:
            ctx.logger.warning(
                "No handler registered for client message type '%s'", msg_type
            )
            return
        await handler(message, ctx)

    @property
    def registered_types(self) -> list[str]:
        return sorted(self._handlers.keys())
