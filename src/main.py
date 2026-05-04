from __future__ import annotations

import json
import logging
import os
import sys

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Allow imports from project root (config/, prompts/, tools/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from config import list_modes
from prompts import list_prompts
from src.events import client_router
from src.events.base import HandlerContext
from src.session_manager import (
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
    SessionManager,
    get_azure_token,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("realtime-relay")

ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8000").split(",")
    if o.strip()
]
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "10"))

app = FastAPI(title="GPT Realtime Starter Kit")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


manager = SessionManager()


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    try:
        get_azure_token()
        return JSONResponse({"status": "ok"})
    except Exception:
        logger.exception("Health check failed")
        return JSONResponse({"status": "error", "detail": "Health check failed"}, status_code=500)


@app.get("/api/modes")
async def get_modes():
    return JSONResponse({"modes": list_modes()})


@app.get("/api/prompts")
async def get_prompts():
    return JSONResponse({"prompts": list_prompts()})


@app.get("/api/models")
async def get_models():
    """List available Azure OpenAI deployments."""
    try:
        token = get_azure_token()
        endpoint = AZURE_OPENAI_ENDPOINT.rstrip("/")
        url = f"{endpoint}/openai/deployments?api-version=2024-10-21"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

        models = []
        for dep in data.get("data", []):
            models.append({
                "id": dep.get("id", ""),
                "model": dep.get("model", ""),
                "status": dep.get("status", ""),
            })

        # Put the current default first
        models.sort(key=lambda m: (0 if m["id"] == AZURE_OPENAI_DEPLOYMENT else 1, m["id"]))

        return JSONResponse({"models": models, "default": AZURE_OPENAI_DEPLOYMENT})
    except Exception as e:
        logger.exception("Failed to list models")
        return JSONResponse({
            "models": [{
                "id": AZURE_OPENAI_DEPLOYMENT,
                "model": AZURE_OPENAI_DEPLOYMENT,
                "status": "unknown",
            }],
            "default": AZURE_OPENAI_DEPLOYMENT,
            "error": "Failed to list deployments",
        })


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    mode: str = "voice_assistant",
    prompt: str = "default",
    model: str | None = None,
):
    logger.info("Client connecting — session=%s, mode=%s, prompt=%s, model=%s", session_id, mode, prompt, model or "default")

    if len(manager.active_sessions) >= MAX_SESSIONS:
        await websocket.accept()
        await websocket.send_text(json.dumps({"type": "error", "error": "Maximum concurrent sessions reached"}))
        await websocket.close()
        return

    try:
        await manager.connect(websocket, session_id, mode, prompt, model)
    except FileNotFoundError as e:
        await websocket.accept()
        await websocket.send_text(json.dumps({"type": "error", "error": str(e)}))
        await websocket.close()
        return
    except Exception as e:
        logger.exception("Failed to connect session %s", session_id)
        await websocket.accept()
        await websocket.send_text(json.dumps({"type": "error", "error": "Connection failed"}))
        await websocket.close()
        return

    logger.info("Session %s connected", session_id)

    ctx = HandlerContext(
        session_id=session_id,
        manager=manager,
        websocket=websocket,
        logger=logger,
    )

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON from session %s", session_id)
                continue

            await client_router.dispatch(message, ctx)

    except WebSocketDisconnect:
        logger.info("Client disconnected — session=%s", session_id)
    except Exception as e:
        logger.exception("WebSocket error for session %s: %s", session_id, e)
    finally:
        await manager.disconnect(session_id)
        logger.info("Session %s cleaned up", session_id)


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
