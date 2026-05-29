# LLM Wiki pattern (reference)

This project adopts the **LLM Wiki** idea: instead of only retrieving raw chunks at query time, an agent **incrementally builds and maintains** a structured, interlinked set of markdown pages—so knowledge **compounds** across sessions.

**Original write-up:** [karpathy/llm-wiki.md gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## Core idea (summary)

- **Raw sources:** curated inputs you add (this repo: `raw/`).
- **Wiki:** agent-owned markdown with cross-references and synthesis (this repo: `wiki/`).
- **Schema:** rules for ingest, query, and lint (this repo: `AGENTS.md`).

## Operations

- **Ingest:** Read sources → update wiki pages → refresh `index.md` → append `log.md`.
- **Query:** Read `index.md`, drill into pages, cite paths; file durable answers back into the wiki when useful.
- **Lint:** Contradictions, stale claims, orphans, missing cross-links; record in `log.md`.

## Optional tooling

The gist mentions optional search (for example [qmd](https://github.com/tobi/qmd)) when `index.md` is no longer enough at scale.

This repo also ships a **local SQLite + FTS5** index over markdown: see [`knowledge/README.md`](../knowledge/README.md) and run `py -3 knowledge/scripts/sync_sqlite.py` after wiki edits. Use **Obsidian** on `wiki/` for graph navigation; use the DB for fast keyword/BM25 retrieval (e.g. future voice tools).
