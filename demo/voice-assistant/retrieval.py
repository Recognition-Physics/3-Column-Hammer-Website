"""Retrieval for the Hammer voice demo — delegates to `knowledge.retriever`."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from knowledge.retriever import ALLOWED_WIKI_FILES, Chunk, KnowledgeRetriever, WikiRetriever

__all__ = ["ALLOWED_WIKI_FILES", "Chunk", "KnowledgeRetriever", "WikiRetriever"]
