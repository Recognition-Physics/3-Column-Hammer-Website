# Company knowledge (LLM Wiki + SQLite)

This folder implements [Karpathy’s **LLM Wiki** pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): **raw sources**, a **markdown wiki** humans browse, and a **schema** agents follow—plus a **SQLite + FTS5** index for fast keyword search (the gist’s “optional CLI tools / search engine” layer).

## Obsidian (visualize everything)

1. In Obsidian: **Open folder as vault** → choose this repository root (`VibeVoice`), or only the `wiki/` folder if you want a smaller vault.
2. Use **Graph view** for `[[wikilinks]]` between pages; keep canonical narrative in `wiki/index.md` and domain pages under `wiki/`.
3. Optional: install **Dataview** and add YAML frontmatter (`voice`, `status`, `tags`) to pages you want dashboards for.
4. After each DB rebuild, open `knowledge/generated/db_coverage.md` (generated locally) to see **which markdown files and chunk counts** are inside the SQLite index.

## Build the SQLite index

From the repo root (requires Python 3.10+):

```powershell
py -3 knowledge\scripts\sync_sqlite.py
```

Defaults:

- Wiki root: `wiki/` (voice-demo **allowlist** only — same pages as `company-voice-demo-canonical.md`)
- Hammer raw: `raw/hammer-data/` (all `*.md`, recursive)
- Database: `knowledge/data/company_kb.sqlite` (ignored by git—see `knowledge/data/.gitignore`)

Voice demos call `knowledge/kb_bootstrap.py` on startup if the DB is missing. Retrieval (`knowledge/retriever.py`) uses SQLite FTS5 BM25, query expansion (product names / synonyms), multi-query fusion, and fallbacks so conversational questions still return grounded passages.

Override paths:

```powershell
py -3 knowledge\scripts\sync_sqlite.py --wiki-dir wiki --hammer-raw-dir raw\hammer-data --db knowledge\data\company_kb.sqlite
```

Index every wiki page (not only the demo allowlist):

```powershell
py -3 knowledge\scripts\sync_sqlite.py --full-wiki
```

Smoke test without the main wiki tree:

```powershell
py -3 knowledge\scripts\sync_sqlite.py --wiki-dir knowledge\fixtures\mini_wiki
```

## Query examples (FTS5)

```sql
-- keyword search over chunked text (lower latency than re-reading all md files)
SELECT d.path, d.title, snippet(kb_chunk_fts, 0, '[', ']', '…', 32) AS excerpt, bm25(kb_chunk_fts) AS rank
FROM kb_chunk_fts
JOIN kb_chunk c ON c.id = kb_chunk_fts.rowid
JOIN kb_document d ON d.id = c.document_id
WHERE kb_chunk_fts MATCH 'dealership'
ORDER BY rank
LIMIT 8;
```

Run with the SQLite CLI, or any SQLite browser pointing at `knowledge/data/company_kb.sqlite`.

## Tables

| Table | Role |
|-------|------|
| `kb_document` | One row per markdown page (path, title, full body, hash). |
| `kb_chunk` | Chunked body text for retrieval-sized segments. |
| `kb_chunk_fts` | FTS5 inverted index over chunk text (BM25 ranking). |
| `kb_product` | Structured product rows (seeded with examples; extend as needed). |
| `kb_sync` | Last successful sync metadata. |

## Where raw sources live

Immutable “layer 1” in the gist sense stays in this repo under [`raw/`](../raw/) (for example `raw/hammer-data/`). The wiki under [`wiki/`](../wiki/) is the compiled, cross-linked layer Obsidian should focus on.
