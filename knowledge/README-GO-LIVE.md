# knowledge/ — AI search index (bundled on deploy)

SQLite database used when the voice agent calls `search_wiki`.

- **You usually do not edit this for go-live** — Vercel bundles `wiki/` and `raw/hammer-data/`; the index is built at runtime or included via `vercel.json`.
- **Deep docs:** see **`README.md`** in this folder (Obsidian, rebuild scripts).

For deployment, focus on repo root **`GO-LIVE-VERCEL.md`** instead.
