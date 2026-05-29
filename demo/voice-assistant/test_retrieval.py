"""Smoke tests: grounded retrieval over wiki + hammer-data (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from knowledge.kb_bootstrap import ensure_kb_database  # noqa: E402
from knowledge.retriever import KnowledgeRetriever  # noqa: E402

QUERIES = [
    ("Hammer dealership CRM lead follow-up", {"entity-hammer-ai.md", "raw/hammer-data"}),
    ("Facebook ads inventory meta", {"raw/hammer-data"}),
    ("MarketPoster chrome extension marketplace", {"raw/hammer-data", "entity-hammer-ai.md"}),
    ("Hammer Connect marketplace SMS text", {"raw/hammer-data", "entity-hammer-ai.md"}),
    ("VinSolutions CDK integration CRM", {"entity-hammer-ai.md", "raw/hammer-data"}),
    ("after hours leads 48 percent", {"entity-hammer-ai.md", "raw/hammer-data"}),
    ("agentic call transcript voicemail", {"entity-hammer-ai.md", "raw/hammer-data"}),
]


def main() -> None:
    ensure_kb_database(ROOT, force=True)
    wiki = ROOT / "wiki"
    hammer = ROOT / "raw" / "hammer-data"
    db = ROOT / "knowledge" / "data" / "company_kb.sqlite"
    r = KnowledgeRetriever(wiki, hammer_raw_dir=hammer if hammer.is_dir() else None, db_path=db)
    assert db.is_file(), "expected SQLite KB after ensure_kb_database"

    for q, expect_prefixes in QUERIES:
        pairs = r.search(q, k=6)
        assert pairs, f"expected hits for: {q!r}"
        docs = {c.doc_id for c, _ in pairs}
        assert any(
            any(doc == p or doc.startswith(p) for p in expect_prefixes) for doc in docs
        ), f"{q!r} -> {docs} (wanted one of {expect_prefixes})"
        print(f"OK {q!r} -> {list(docs)[:3]}")

    # Conversational phrasing should still return passages (NotebookLM-style: never empty).
    vague = r.search("tell me how your facebook thing works for dealers", k=4)
    assert vague, "vague query should still return grounded passages"
    print("ok")


if __name__ == "__main__":
    main()
