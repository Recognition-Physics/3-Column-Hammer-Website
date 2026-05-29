"""FastAPI server for the Hammer wiki-grounded voice demo (browser push-to-talk)."""

from __future__ import annotations

import os
import sys
import threading
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from llm_client import complete_chat
from retrieval import WikiRetriever

_SHARED_DIR = Path(__file__).resolve().parent.parent / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))
from site_copy import load_site_copy  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_WIKI_DIR = REPO_ROOT / "wiki"
DEFAULT_KB_DB = REPO_ROOT / "knowledge" / "data" / "company_kb.sqlite"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from knowledge.kb_bootstrap import ensure_kb_database  # noqa: E402
from knowledge.learning.pipeline import schedule_after_turn  # noqa: E402


class ChatRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=4000)


class Source(BaseModel):
    doc_id: str
    chunk_id: int
    score: float
    preview: str


class ChatResponse(BaseModel):
    reply: str
    sources: list[Source]


class TtsRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    voice: str | None = Field(None, description="VibeVoice preset stem, e.g. en-Emma_woman")


_tts_lock = threading.Lock()


def _hammer_raw_dir_for_retrieval() -> Path | None:
    """Optional markdown corpus under `raw/hammer-data/` (repo-relative unless overridden)."""
    override = os.environ.get("VOICE_DEMO_HAMMER_RAW_DIR", "").strip()
    if override:
        p = Path(override).expanduser().resolve()
        return p if p.is_dir() else None
    if os.environ.get("VOICE_DEMO_INCLUDE_HAMMER_RAW", "1").strip().lower() in ("0", "false", "no"):
        return None
    p = REPO_ROOT / "raw" / "hammer-data"
    return p if p.is_dir() else None


@lru_cache(maxsize=1)
def get_retriever() -> WikiRetriever:
    wiki_dir = Path(os.environ.get("VOICE_DEMO_WIKI_DIR", str(DEFAULT_WIKI_DIR))).resolve()
    db = Path(os.environ.get("VOICE_DEMO_KB_DB", str(DEFAULT_KB_DB))).resolve()
    pb_env = os.environ.get("VOICE_DEMO_PLAYBOOK_MD", "").strip()
    playbook_md_path = Path(pb_env).expanduser().resolve() if pb_env else None
    return WikiRetriever(
        wiki_dir,
        hammer_raw_dir=_hammer_raw_dir_for_retrieval(),
        db_path=db,
        playbook_md_path=playbook_md_path,
    )


def invalidate_voice_demo_retriever_cache() -> None:
    get_retriever.cache_clear()


def _top_k() -> int:
    try:
        return max(1, min(12, int(os.environ.get("VOICE_DEMO_TOP_K", "8"))))
    except ValueError:
        return 8


def _tts_max_chars() -> int:
    try:
        return max(200, min(8000, int(os.environ.get("VOICE_DEMO_TTS_MAX_CHARS", "2000"))))
    except ValueError:
        return 2000


@asynccontextmanager
async def _lifespan(app: FastAPI):
    ensure_kb_database(REPO_ROOT)
    get_retriever()
    app.state.vibe_tts = None
    app.state.vibe_tts_error = None
    mode = os.environ.get("VOICE_DEMO_TTS", "vibevoice").strip().lower()
    if mode != "browser":
        try:
            from vibevoice_tts import load_vibevoice_tts

            print("[startup] Loading VibeVoice Realtime TTS (first run may download weights)...")
            app.state.vibe_tts = load_vibevoice_tts()
            print("[startup] VibeVoice TTS ready.")
        except Exception as exc:  # pragma: no cover - environment dependent
            app.state.vibe_tts_error = repr(exc)
            print("[startup] VibeVoice TTS unavailable:", exc)
    yield


app = FastAPI(title="Hammer voice demo", version="0.1.0", lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("VOICE_DEMO_CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _playback_rate() -> float:
    try:
        r = float(os.environ.get("VOICE_DEMO_PLAYBACK_RATE", "1.2"))
    except ValueError:
        r = 1.0
    return max(0.75, min(2.0, r))


@app.get("/api/health")
def health() -> dict:
    tts = getattr(app.state, "vibe_tts", None)
    err = getattr(app.state, "vibe_tts_error", None)
    try:
        tts_steps = int(os.environ.get("VOICE_DEMO_VIBEVOICE_STEPS", "4"))
    except ValueError:
        tts_steps = 4
    return {
        "ok": True,
        "wiki_dir": str(DEFAULT_WIKI_DIR),
        "kb_db": str(DEFAULT_KB_DB),
        "kb_db_exists": DEFAULT_KB_DB.is_file(),
        "vibevoice_tts_loaded": tts is not None,
        "vibevoice_tts_error": err,
        "tts_mode": os.environ.get("VOICE_DEMO_TTS", "vibevoice"),
        "playback_rate": _playback_rate(),
        "vibevoice_diffusion_steps": max(2, min(12, tts_steps)),
    }


@app.get("/api/site_copy")
def site_copy() -> dict:
    wiki_dir = Path(os.environ.get("VOICE_DEMO_WIKI_DIR", str(DEFAULT_WIKI_DIR))).resolve()
    try:
        return load_site_copy(wiki_dir)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    q = body.transcript.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty transcript")

    retriever = get_retriever()
    pairs = retriever.top_k(q, k=_top_k())

    try:
        reply = complete_chat(pairs, q)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"LLM backend error: {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    sources = [
        Source(doc_id=c.doc_id, chunk_id=c.chunk_id, score=round(s, 4), preview=c.text[:220] + ("…" if len(c.text) > 220 else ""))
        for c, s in pairs
    ]
    best_score = float(pairs[0][1]) if pairs else 0.0
    schedule_after_turn(
        REPO_ROOT,
        user_text=q,
        assistant_text=reply,
        retrieval_best_score=best_score,
        channel="voice-assistant",
        cache_clear=invalidate_voice_demo_retriever_cache,
    )
    return ChatResponse(reply=reply, sources=sources)


@app.post("/api/tts")
def synthesize_speech(body: TtsRequest) -> Response:
    """Synthesize reply text to WAV using VibeVoice-Realtime (mono 24 kHz)."""
    svc = getattr(app.state, "vibe_tts", None)
    if svc is None:
        err = getattr(app.state, "vibe_tts_error", None) or "unknown"
        raise HTTPException(
            status_code=503,
            detail=(
                "VibeVoice TTS is not loaded. Install torch/GPU deps and voice presets under "
                "demo/voices/streaming_model, or set VOICE_DEMO_TTS=browser. Last error: "
                + str(err)
            ),
        )

    raw = body.text.strip()
    cap = _tts_max_chars()
    if len(raw) > cap:
        raw = raw[: cap].rstrip() + "…"

    try:
        from vibevoice_tts import synthesize_wav

        with _tts_lock:
            wav = synthesize_wav(svc, raw, voice_key=body.voice)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {exc}") from exc

    return Response(content=wav, media_type="audio/wav")


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index_page() -> FileResponse:
    index = STATIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(status_code=500, detail=f"Missing {index}")
    return FileResponse(index, media_type="text/html; charset=utf-8")
