"""Event handling package.

Exposes two singleton routers:
- ``server_router`` — dispatches SDK ``RealtimeSessionEvent`` to per-type
  handlers that produce JSON-serializable payloads forwarded to the client.
- ``client_router`` — dispatches parsed browser WebSocket messages to
  per-type handlers that act on the active ``RealtimeSession`` via the
  shared session manager.
"""

from src.events.handlers import client_router, server_router

__all__ = ["server_router", "client_router"]
