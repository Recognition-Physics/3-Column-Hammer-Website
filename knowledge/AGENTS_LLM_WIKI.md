# LLM Wiki schema (this repo)

This file is the **schema layer** from [Karpathy’s LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): conventions for maintaining the markdown wiki and keeping it consistent with retrieval.

## Directory roles

- **`raw/`** (repo root): immutable sources (PDFs/MD exports, transcripts). Do not rewrite history here; add new files when new evidence arrives.
- **`wiki/`**: synthesized, interlinked markdown. Prefer updating existing entity/concept pages over duplicating facts.
- **`knowledge/data/company_kb.sqlite`**: generated FTS index over `wiki/` (or another markdown root you pass to the sync script). Safe to delete; rebuild with `knowledge/scripts/sync_sqlite.py`.

## Voice / customer safety

- Pages that are **safe for customer-facing demos** should be explicitly allowlisted in [`wiki/company-voice-demo-canonical.md`](../wiki/company-voice-demo-canonical.md) (see also `demo/voice-assistant/retrieval.py`).
- Use frontmatter tags such as `voice: published` vs `voice: internal` where helpful; Obsidian Dataview can list `voice: published` only.

## Ingest workflow (human + agent)

1. Add or update sources under `raw/…`.
2. Summarize and integrate into `wiki/` (entity pages, `index.md`, append a dated entry to `wiki/log.md`).
3. Run `py -3 knowledge/scripts/sync_sqlite.py` so the SQLite index matches the wiki on disk.

## Lint reminders (periodic)

- Orphan pages (no inbound `[[wikilinks]]` from `index.md` or hubs).
- Contradictions between entity pages and newer raw sources.
- Missing entries in `wiki/index.md` for new pages.
