"""Session manager for realtime WebSocket clients.

Owns the per-client state and the bidirectional pump between browser
WebSockets and Azure OpenAI Realtime sessions.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from fastapi import WebSocket

from azure.identity import DefaultAzureCredential

from agents.realtime import RealtimeRunner, RealtimeSession
from agents.realtime.config import RealtimeUserInputMessage
from agents.realtime.model import RealtimeModelConfig
from agents.realtime.model_inputs import RealtimeModelSendRawMessage

from config import load_session_config
from src.agent import get_agent
from src.events import server_router
from src.events.base import HandlerContext

logger = logging.getLogger("realtime-relay")

AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-realtime-1-5")

_credential = DefaultAzureCredential()


def get_azure_token() -> str:
    token = _credential.get_token("https://cognitiveservices.azure.com/.default")
    return token.token


def _build_realtime_url(deployment: str | None = None) -> str:
    dep = deployment or AZURE_OPENAI_DEPLOYMENT
    host = AZURE_OPENAI_ENDPOINT.rstrip("/")
    # Ensure wss:// scheme (required by the Agents SDK websockets transport)
    host = host.replace("https://", "wss://").replace("http://", "ws://")
    if not host.startswith("ws"):
        host = f"wss://{host}"
    return f"{host}/openai/v1/realtime?model={dep}"


def _build_model_settings(mode: str, deployment: str | None = None) -> dict[str, Any]:
    """Translate YAML config into SDK RealtimeSessionModelSettings."""
    cfg = load_session_config(mode)

    model_name = deployment or AZURE_OPENAI_DEPLOYMENT
    settings: dict[str, Any] = {"model_name": model_name}

    # Output modalities
    modalities = cfg.get("modalities", ["text", "audio"])
    if "audio" in modalities:
        settings["output_modalities"] = ["audio"]
    else:
        settings["output_modalities"] = ["text"]

    # Audio nested structure (preferred by SDK)
    audio_input: dict[str, Any] = {}
    audio_output: dict[str, Any] = {}

    # Input format
    in_fmt = cfg.get("input_audio_format", "pcm16")
    audio_input["format"] = in_fmt

    # Turn detection
    td = cfg.get("turn_detection")
    if td is None:
        audio_input["turn_detection"] = None
    elif isinstance(td, dict):
        td_type = td.get("type", "server_vad")
        if td_type == "semantic_vad":
            clean_td: dict[str, Any] = {"type": "semantic_vad"}
            if "eagerness" in td:
                clean_td["eagerness"] = td["eagerness"]
        else:
            clean_td = {k: v for k, v in td.items() if k in (
                "type", "threshold", "prefix_padding_ms",
                "silence_duration_ms", "create_response", "interrupt_response",
            )}
        audio_input["turn_detection"] = clean_td

    # Input transcription
    transcription = cfg.get("input_audio_transcription")
    if transcription:
        audio_input["transcription"] = transcription

    # Output format
    out_fmt = cfg.get("output_audio_format", "pcm16")
    audio_output["format"] = out_fmt

    # Voice
    voice = cfg.get("voice")
    if voice:
        audio_output["voice"] = voice

    settings["audio"] = {}
    if audio_input:
        settings["audio"]["input"] = audio_input
    if audio_output:
        settings["audio"]["output"] = audio_output

    return settings


class SessionManager:
    """Manages SDK RealtimeSessions for connected browser clients."""

    def __init__(self) -> None:
        self.active_sessions: dict[str, RealtimeSession] = {}
        self.session_contexts: dict[str, Any] = {}
        self.websockets: dict[str, WebSocket] = {}

    async def connect(
        self,
        websocket: WebSocket,
        session_id: str,
        mode: str = "voice_assistant",
        prompt: str = "default",
        model: str | None = None,
    ) -> None:
        await websocket.accept()
        self.websockets[session_id] = websocket

        agent = get_agent(prompt)
        runner = RealtimeRunner(agent)

        token = get_azure_token()
        model_config: RealtimeModelConfig = {
            "url": _build_realtime_url(model),
            "headers": {"authorization": f"Bearer {token}"},
            "initial_model_settings": _build_model_settings(mode, model),
        }

        session_context = await runner.run(model_config=model_config)
        session = await session_context.__aenter__()
        self.active_sessions[session_id] = session
        self.session_contexts[session_id] = session_context

        asyncio.create_task(self._process_events(session_id))

    async def disconnect(self, session_id: str) -> None:
        if session_id in self.session_contexts:
            await self.session_contexts[session_id].__aexit__(None, None, None)
            del self.session_contexts[session_id]
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        if session_id in self.websockets:
            del self.websockets[session_id]

    async def send_audio(self, session_id: str, audio_bytes: bytes) -> None:
        if session_id in self.active_sessions:
            await self.active_sessions[session_id].send_audio(audio_bytes)

    async def send_client_event(self, session_id: str, event: dict[str, Any]) -> None:
        session = self.active_sessions.get(session_id)
        if not session:
            return
        await session.model.send_event(
            RealtimeModelSendRawMessage(
                message={
                    "type": event["type"],
                    **{k: v for k, v in event.items() if k != "type"},
                }
            )
        )

    async def send_user_message(
        self, session_id: str, message: RealtimeUserInputMessage
    ) -> None:
        session = self.active_sessions.get(session_id)
        if not session:
            return
        await session.send_message(message)

    async def interrupt(self, session_id: str) -> None:
        session = self.active_sessions.get(session_id)
        if not session:
            return
        await session.interrupt()

    # -- Event processing --------------------------------------------------

    async def _process_events(self, session_id: str) -> None:
        try:
            session = self.active_sessions[session_id]
            websocket = self.websockets[session_id]
            ctx = HandlerContext(
                session_id=session_id,
                manager=self,
                websocket=websocket,
                logger=logger,
            )

            async for event in session:
                payload = await server_router.dispatch(event, ctx)
                if payload is not None:
                    await websocket.send_text(json.dumps(payload))
        except Exception as e:
            logger.error("Error processing events for %s: %s", session_id, e)
