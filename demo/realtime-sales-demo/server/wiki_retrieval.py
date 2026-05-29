"""Retrieval for the Hammer Realtime demo — delegates to `knowledge.retriever`."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    env = os.environ.get("REALTIME_SALES_REPO_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    # Local layout: .../<repo>/demo/realtime-sales-demo/server/wiki_retrieval.py
    return Path(__file__).resolve().parents[3]


_REPO = _repo_root()
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from knowledge.retriever import ALLOWED_WIKI_FILES, Chunk, KnowledgeRetriever, WikiRetriever

__all__ = ["ALLOWED_WIKI_FILES", "Chunk", "KnowledgeRetriever", "WikiRetriever"]
