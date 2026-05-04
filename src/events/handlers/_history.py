"""Shared helpers for history-related handlers."""

from __future__ import annotations

from typing import Any

from agents.realtime.items import RealtimeItem


def sanitize_history_item(item: RealtimeItem) -> dict[str, Any]:
    """Strip raw audio bytes from a history item before sending to the client."""
    item_dict = item.model_dump()
    content = item_dict.get("content")
    if isinstance(content, list):
        sanitized: list[Any] = []
        for part in content:
            if isinstance(part, dict):
                p = part.copy()
                if p.get("type") in ("audio", "input_audio"):
                    p.pop("audio", None)
                sanitized.append(p)
            else:
                sanitized.append(part)
        item_dict["content"] = sanitized
    return item_dict
